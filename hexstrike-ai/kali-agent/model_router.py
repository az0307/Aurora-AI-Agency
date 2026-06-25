"""
ModelRouter — Routes tasks between GLM-4.5 (HexStrike local) and Claude Sonnet (API)
Provides /interpret endpoint for HexStrike integration.

GLM-4.5 handles: tool call decisions, command parameter generation, session state, raw output parsing
Sonnet handles:  playbook generation (Curator), finding analysis, report writing, natural language interpretation

AutoBoros.ai | 2026-03-27
"""

import json
import os
import re
from typing import Optional
from dataclasses import dataclass, field

# Try importing zhipuai for GLM-4.5 (HexStrike native model)
try:
    from zhipuai import ZhipuAI
    GLM_AVAILABLE = True
except ImportError:
    GLM_AVAILABLE = False

# Try importing anthropic for Sonnet
try:
    import anthropic
    SONNET_AVAILABLE = True
except ImportError:
    SONNET_AVAILABLE = False


@dataclass
class RoutingDecision:
    """Result of the routing decision."""
    model: str                     # "glm-4.5" or "sonnet"
    reason: str                    # Why this model was chosen
    task_type: str                 # Classified task type
    fallback: Optional[str] = None # If primary model unavailable


# Task type → model mapping
ROUTING_TABLE = {
    # GLM-4.5 (fast, local, good at structured tasks)
    "command_generation":    RoutingDecision("glm-4.5", "Structured command output", "command_generation", "sonnet"),
    "parameter_extraction":  RoutingDecision("glm-4.5", "Extract params from context", "parameter_extraction", "sonnet"),
    "output_parsing":        RoutingDecision("glm-4.5", "Parse raw tool output", "output_parsing", "sonnet"),
    "session_state":         RoutingDecision("glm-4.5", "Manage session state", "session_state", "sonnet"),
    "tool_selection":        RoutingDecision("glm-4.5", "Decide which tool to run", "tool_selection", "sonnet"),
    "json_transformation":   RoutingDecision("glm-4.5", "Transform data formats", "json_transformation", "sonnet"),

    # Sonnet (stronger reasoning, better writing, Curator role)
    "playbook_generation":   RoutingDecision("sonnet", "Complex planning/reasoning", "playbook_generation", "glm-4.5"),
    "finding_analysis":      RoutingDecision("sonnet", "Nuanced security analysis", "finding_analysis", "glm-4.5"),
    "finding_triage":        RoutingDecision("sonnet", "Priority assessment", "finding_triage", "glm-4.5"),
    "report_writing":        RoutingDecision("sonnet", "Natural language generation", "report_writing", "glm-4.5"),
    "executive_summary":     RoutingDecision("sonnet", "Business-focused writing", "executive_summary", "glm-4.5"),
    "remediation_advice":    RoutingDecision("sonnet", "Context-aware recommendations", "remediation_advice", "glm-4.5"),
    "attack_narrative":      RoutingDecision("sonnet", "Storytelling + technical accuracy", "attack_narrative", "glm-4.5"),
    "scope_interpretation":  RoutingDecision("sonnet", "Natural language → scope config", "scope_interpretation", "glm-4.5"),
    "user_interaction":      RoutingDecision("sonnet", "Conversational response", "user_interaction", "glm-4.5"),
}

# Keywords that trigger specific task types
TASK_CLASSIFIERS = {
    "command_generation": ["generate command", "what command", "nmap flags", "run nmap", "construct", "build command"],
    "parameter_extraction": ["extract", "parse parameters", "get params from"],
    "output_parsing": ["parse output", "interpret results", "what does this mean", "analyze output"],
    "tool_selection": ["which tool", "what tool should", "best tool for", "select tool"],
    "playbook_generation": ["create playbook", "generate plan", "plan the engagement", "what steps"],
    "finding_analysis": ["analyze finding", "assess vulnerability", "how critical", "impact analysis"],
    "finding_triage": ["prioritize", "triage", "rank findings", "most critical"],
    "report_writing": ["write report", "generate report", "document findings", "create deliverable"],
    "executive_summary": ["executive summary", "non-technical", "for leadership", "business impact"],
    "remediation_advice": ["how to fix", "remediation", "patch", "mitigate", "recommend"],
    "attack_narrative": ["attack story", "attack path", "how we got in", "narrative"],
    "scope_interpretation": ["define scope", "parse scope", "interpret authorization"],
    "user_interaction": ["explain", "help me", "what is", "how do I"],
}


class ModelRouter:
    """Routes tasks to the optimal model based on task classification."""

    def __init__(
        self,
        glm_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        default_model: str = "sonnet",
    ):
        self.default_model = default_model

        # Initialize GLM client
        self.glm_client = None
        if GLM_AVAILABLE and glm_api_key:
            self.glm_client = ZhipuAI(api_key=glm_api_key)

        # Initialize Sonnet client
        self.sonnet_client = None
        if SONNET_AVAILABLE and anthropic_api_key:
            self.sonnet_client = anthropic.Anthropic(api_key=anthropic_api_key)

    def classify_task(self, prompt: str, context: Optional[dict] = None) -> str:
        """Classify a task based on prompt content."""
        prompt_lower = prompt.lower()

        # Check each classifier
        best_match = None
        best_score = 0

        for task_type, keywords in TASK_CLASSIFIERS.items():
            score = sum(1 for kw in keywords if kw in prompt_lower)
            if score > best_score:
                best_score = score
                best_match = task_type

        # If no keyword match, use heuristics
        if not best_match or best_score == 0:
            # Short prompts with tool names → command generation
            if len(prompt.split()) < 20 and any(
                tool in prompt_lower
                for tool in ["nmap", "nuclei", "sqlmap", "ffuf", "gobuster", "hydra"]
            ):
                return "command_generation"

            # Contains JSON or structured data → parsing
            if prompt.strip().startswith("{") or prompt.strip().startswith("["):
                return "output_parsing"

            # Long prose → probably needs Sonnet
            if len(prompt.split()) > 50:
                return "report_writing"

            return "user_interaction"

        return best_match

    def route(self, prompt: str, context: Optional[dict] = None) -> RoutingDecision:
        """Determine which model should handle this task."""
        task_type = self.classify_task(prompt, context)
        decision = ROUTING_TABLE.get(task_type)

        if not decision:
            return RoutingDecision(self.default_model, "Default routing", "unknown")

        # Check model availability and fall back if needed
        if decision.model == "glm-4.5" and not self.glm_client:
            if decision.fallback and self.sonnet_client:
                return RoutingDecision(
                    decision.fallback,
                    f"GLM unavailable, falling back to {decision.fallback}",
                    decision.task_type,
                )
        elif decision.model == "sonnet" and not self.sonnet_client:
            if decision.fallback and self.glm_client:
                return RoutingDecision(
                    decision.fallback,
                    f"Sonnet unavailable, falling back to {decision.fallback}",
                    decision.task_type,
                )

        return decision

    async def interpret(self, step: dict, context: dict) -> dict:
        """
        /interpret endpoint — takes a playbook step + context, returns a shell command.
        This is the bridge between Curator playbooks and actual tool execution.

        Args:
            step: Playbook step with skill, action, params
            context: Engagement context (target, scope, prior results)

        Returns:
            {
                "command": ["nmap", "-sV", "10.0.0.1"],
                "tool": "nmap",
                "reasoning": "Why this command was chosen",
                "approval_required": false,
                "timeout": 300
            }
        """
        # Build the interpretation prompt
        prompt = f"""You are a penetration testing assistant. Given this playbook step and context,
generate the exact command to execute.

STEP:
  Skill: {step.get('skill', 'unknown')}
  Action: {step.get('action', 'unknown')}
  Params: {json.dumps(step.get('params', {}), indent=2)}

CONTEXT:
  Target: {context.get('target', 'unknown')}
  Phase: {context.get('phase', 'unknown')}
  Prior findings: {json.dumps(context.get('findings', [])[:5], indent=2)}

Respond with ONLY a JSON object:
{{
  "command": ["tool", "arg1", "arg2"],
  "tool": "tool_name",
  "reasoning": "one sentence why",
  "approval_required": true/false,
  "timeout": seconds
}}"""

        decision = self.route(prompt, context)

        try:
            if decision.model == "glm-4.5" and self.glm_client:
                response = self.glm_client.chat.completions.create(
                    model="glm-4-plus",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                raw = response.choices[0].message.content

            elif decision.model == "sonnet" and self.sonnet_client:
                response = self.sonnet_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = response.content[0].text

            else:
                return {
                    "error": "No model available",
                    "decision": decision.model,
                    "step": step,
                }

            # Parse response
            clean = re.sub(r'```json\s*|```\s*', '', raw).strip()
            result = json.loads(clean)
            result["routed_to"] = decision.model
            result["routing_reason"] = decision.reason
            return result

        except Exception as e:
            return {
                "error": str(e),
                "routed_to": decision.model,
                "step": step,
            }

    def get_routing_stats(self) -> dict:
        """Return model availability and routing table info."""
        return {
            "glm_available": self.glm_client is not None,
            "sonnet_available": self.sonnet_client is not None,
            "default_model": self.default_model,
            "task_types": len(ROUTING_TABLE),
            "glm_tasks": [k for k, v in ROUTING_TABLE.items() if v.model == "glm-4.5"],
            "sonnet_tasks": [k for k, v in ROUTING_TABLE.items() if v.model == "sonnet"],
        }


# --- Flask endpoint for HexStrike integration ---

def register_interpret_endpoint(app):
    """Register the /interpret endpoint on a Flask app."""
    from flask import request, jsonify

    router = ModelRouter(
        glm_api_key=os.environ.get("ZHIPUAI_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    @app.route("/interpret", methods=["POST"])
    def interpret():
        data = request.get_json()
        step = data.get("step", {})
        context = data.get("context", {})

        import asyncio
        result = asyncio.run(router.interpret(step, context))
        return jsonify(result)

    @app.route("/routing/stats", methods=["GET"])
    def routing_stats():
        return jsonify(router.get_routing_stats())

    @app.route("/routing/classify", methods=["POST"])
    def classify():
        data = request.get_json()
        prompt = data.get("prompt", "")
        task_type = router.classify_task(prompt)
        decision = router.route(prompt)
        return jsonify({
            "task_type": task_type,
            "model": decision.model,
            "reason": decision.reason,
            "fallback": decision.fallback,
        })
