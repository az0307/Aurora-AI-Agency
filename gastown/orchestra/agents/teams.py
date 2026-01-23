"""
Team Structures for Mayor
Advisor, Utility, and Prompting teams
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class TeamType(Enum):
    ADVISOR = "advisor"  # Strategic guidance and planning
    UTILITY = "utility"  # Tools and specialized utilities
    PROMPTING = "prompting"  # Prompt engineering and thinking methods
    EXECUTION = "execution"  # Workers and specialists


class Team:
    """Represents a team of agents"""

    def __init__(self, name: str, team_type: TeamType, specialty: str = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.team_type = team_type
        self.specialty = specialty
        self.members: List[str] = []  # Agent IDs
        self.created_at = datetime.now().isoformat()
        self.metadata = {}

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "team_type": self.team_type.value,
            "specialty": self.specialty,
            "members": self.members,
            "created_at": self.created_at,
            "metadata": self.metadata
        }


class AdvisorAgent:
    """
    Advisor Agent - Provides strategic guidance to Mayor
    """

    def __init__(self, name: str, specialty: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = "advisor"
        self.specialty = specialty  # planning, architecture, optimization, risk
        self.status = "idle"
        self.created_at = datetime.now().isoformat()
        self.advice_given = 0

    def analyze_task(self, task: Dict) -> Dict:
        """Analyze a task and provide strategic advice"""
        advice = {
            "advisor_id": self.id,
            "advisor_name": self.name,
            "specialty": self.specialty,
            "timestamp": datetime.now().isoformat()
        }

        if self.specialty == "planning":
            advice["recommendations"] = self._planning_advice(task)
        elif self.specialty == "architecture":
            advice["recommendations"] = self._architecture_advice(task)
        elif self.specialty == "optimization":
            advice["recommendations"] = self._optimization_advice(task)
        elif self.specialty == "risk":
            advice["recommendations"] = self._risk_advice(task)

        self.advice_given += 1
        return advice

    def _planning_advice(self, task: Dict) -> List[str]:
        """Planning-focused advice"""
        return [
            f"Break '{task.get('title')}' into 3-5 major phases",
            "Identify dependencies between subtasks",
            "Consider parallel execution opportunities",
            "Set clear milestones and checkpoints",
            "Estimate resources needed per phase"
        ]

    def _architecture_advice(self, task: Dict) -> List[str]:
        """Architecture-focused advice"""
        return [
            "Consider system design patterns applicable to this task",
            "Identify reusable components",
            "Plan for scalability and maintainability",
            "Define clear interfaces between components",
            "Consider security and performance from the start"
        ]

    def _optimization_advice(self, task: Dict) -> List[str]:
        """Optimization-focused advice"""
        return [
            "Look for opportunities to cache or memoize",
            "Consider algorithmic complexity",
            "Identify bottlenecks early",
            "Profile before optimizing",
            "Balance speed vs. maintainability"
        ]

    def _risk_advice(self, task: Dict) -> List[str]:
        """Risk assessment advice"""
        priority = task.get('priority', 'medium')
        risks = [
            f"Priority: {priority} - adjust resource allocation accordingly",
            "Identify potential failure points",
            "Plan fallback strategies",
            "Consider edge cases and error handling",
            "Set up monitoring and alerts"
        ]

        if priority in ['high', 'critical']:
            risks.append("⚠️ High priority - recommend twin or swarm method for validation")

        return risks

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "specialty": self.specialty,
            "status": self.status,
            "advice_given": self.advice_given,
            "created_at": self.created_at
        }


class UtilityAgent:
    """
    Utility Agent - Provides specialized tools and capabilities
    """

    def __init__(self, name: str, capability: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = "utility"
        self.capability = capability  # web_search, deep_think, browser, computer_use
        self.status = "idle"
        self.created_at = datetime.now().isoformat()
        self.executions = 0

    def execute(self, task: Dict, params: Dict = None) -> Dict:
        """Execute utility function"""
        self.status = "working"
        result = {
            "utility_id": self.id,
            "capability": self.capability,
            "timestamp": datetime.now().isoformat()
        }

        if self.capability == "web_search":
            result["output"] = self._web_search(task, params)
        elif self.capability == "deep_think":
            result["output"] = self._deep_think(task, params)
        elif self.capability == "browser":
            result["output"] = self._agentic_browser(task, params)
        elif self.capability == "computer_use":
            result["output"] = self._computer_use(task, params)

        self.executions += 1
        self.status = "idle"
        return result

    def _web_search(self, task: Dict, params: Dict) -> Dict:
        """Web search capability (integration point)"""
        return {
            "capability": "web_search",
            "description": "Search web for relevant information",
            "integration": "WebSearch tool via Claude Code",
            "query": f"Best practices for: {task.get('title')}",
            "status": "ready_for_integration",
            "notes": "Would use WebSearch tool to find documentation, examples, solutions"
        }

    def _deep_think(self, task: Dict, params: Dict) -> Dict:
        """Deep thinking capability (extended reasoning)"""
        return {
            "capability": "deep_think",
            "description": "Extended reasoning on complex problems",
            "integration": "Extended thinking budget for Claude",
            "thinking_focus": [
                f"Analyze complexity of: {task.get('title')}",
                "Consider multiple solution approaches",
                "Evaluate trade-offs",
                "Anticipate edge cases",
                "Plan implementation strategy"
            ],
            "status": "ready_for_integration",
            "notes": "Would use extended thinking time for complex reasoning"
        }

    def _agentic_browser(self, task: Dict, params: Dict) -> Dict:
        """Agentic browser capability"""
        return {
            "capability": "agentic_browser",
            "description": "Autonomous web browsing and interaction",
            "integration": "Browser automation via Claude Computer Use",
            "actions": [
                "Navigate to documentation sites",
                "Search for code examples",
                "Read API documentation",
                "Check compatibility matrices",
                "Download resources"
            ],
            "status": "ready_for_integration",
            "notes": "Would use Computer Use tool for browser automation"
        }

    def _computer_use(self, task: Dict, params: Dict) -> Dict:
        """Computer use capability"""
        return {
            "capability": "computer_use",
            "description": "Direct computer interaction and automation",
            "integration": "Claude Computer Use tool",
            "capabilities": [
                "File system operations",
                "Application launching",
                "Screenshot analysis",
                "GUI automation",
                "System monitoring"
            ],
            "status": "ready_for_integration",
            "notes": "Would use Computer Use for system-level tasks"
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "capability": self.capability,
            "status": self.status,
            "executions": self.executions,
            "created_at": self.created_at
        }


class PromptingAgent:
    """
    Prompting Agent - Specialized in prompt engineering and thinking methods
    """

    def __init__(self, name: str, specialty: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = "prompting"
        self.specialty = specialty  # chain_of_thought, few_shot, zero_shot, tree_of_thought
        self.status = "idle"
        self.created_at = datetime.now().isoformat()
        self.prompts_generated = 0

    def generate_enhanced_prompt(self, task: Dict, thinking_method: str) -> str:
        """Generate optimized prompt based on specialty"""
        self.status = "working"

        if self.specialty == "chain_of_thought":
            prompt = self._chain_of_thought_prompt(task, thinking_method)
        elif self.specialty == "few_shot":
            prompt = self._few_shot_prompt(task, thinking_method)
        elif self.specialty == "tree_of_thought":
            prompt = self._tree_of_thought_prompt(task, thinking_method)
        else:
            prompt = self._zero_shot_prompt(task, thinking_method)

        self.prompts_generated += 1
        self.status = "idle"
        return prompt

    def _chain_of_thought_prompt(self, task: Dict, thinking_method: str) -> str:
        """Chain of thought prompting"""
        return f"""Task: {task.get('title')}

Let's approach this step-by-step:

1. First, understand the requirements:
   {task.get('description', 'No description provided')}

2. Then, break down the approach:
   - Identify key components
   - Determine dependencies
   - Plan execution order

3. Next, consider the thinking method: {thinking_method}
   - How does this method apply here?
   - What are the advantages?
   - What coordination is needed?

4. Finally, execute with clear reasoning at each step.

Priority: {task.get('priority', 'medium')}

Think through each step carefully and explain your reasoning.
"""

    def _few_shot_prompt(self, task: Dict, thinking_method: str) -> str:
        """Few-shot prompting with examples"""
        return f"""Task: {task.get('title')}

Here are examples of similar tasks:

Example 1: Building a REST API
- Approach: Define routes → Create controllers → Add middleware → Test endpoints
- Result: Fully functional API with authentication

Example 2: Optimizing database queries
- Approach: Profile queries → Identify bottlenecks → Add indexes → Validate improvement
- Result: 10x performance improvement

Now for your task:
{task.get('description', '')}

Thinking Method: {thinking_method}
Priority: {task.get('priority', 'medium')}

Apply similar patterns and best practices from the examples above.
"""

    def _tree_of_thought_prompt(self, task: Dict, thinking_method: str) -> str:
        """Tree of thought prompting"""
        return f"""Task: {task.get('title')}

Use tree-of-thought reasoning:

Root: {task.get('description', '')}

Branch 1: What are possible approaches?
- Approach A: [Consider pros/cons]
- Approach B: [Consider pros/cons]
- Approach C: [Consider pros/cons]

Branch 2: For each approach, what are the steps?
- Approach A steps: [Detail]
- Approach B steps: [Detail]
- Approach C steps: [Detail]

Branch 3: Evaluate and select best path
- Compare trade-offs
- Consider {task.get('priority', 'medium')} priority
- Factor in {thinking_method} method

Branch 4: Execute selected approach
- Implement with full reasoning
- Validate at each step

Explore all branches before committing to a path.
"""

    def _zero_shot_prompt(self, task: Dict, thinking_method: str) -> str:
        """Zero-shot prompting"""
        return f"""Task: {task.get('title')}

Description: {task.get('description', '')}

Thinking Method: {thinking_method}
Priority: {task.get('priority', 'medium')}

Requirements:
- Solve this task using your expertise
- Apply best practices
- Ensure quality and completeness
- Document your approach

Execute with excellence.
"""

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "specialty": self.specialty,
            "status": self.status,
            "prompts_generated": self.prompts_generated,
            "created_at": self.created_at
        }


class IntegrationPoint:
    """
    Integration points for external tools
    """

    @staticmethod
    def claude_code_config() -> Dict:
        """Configuration for Claude Code integration"""
        return {
            "tool": "claude_code",
            "description": "Anthropic's official CLI for Claude",
            "capabilities": [
                "File operations (Read, Write, Edit)",
                "Code execution (Bash)",
                "Search (Glob, Grep)",
                "Web tools (WebFetch, WebSearch)",
                "Task spawning (nested agents)"
            ],
            "integration_method": "Direct tool calls",
            "status": "available",
            "notes": "Current environment - fully integrated"
        }

    @staticmethod
    def opencode_config() -> Dict:
        """Configuration for OpenCode/Aider integration"""
        return {
            "tool": "aider/opencode",
            "description": "Open source AI coding assistants",
            "options": [
                {"name": "Aider", "strength": "Git-aware coding"},
                {"name": "OpenHands", "strength": "Autonomous agents"},
                {"name": "Cursor", "strength": "IDE integration"}
            ],
            "integration_method": "Subprocess execution",
            "status": "ready_for_integration",
            "command_pattern": "aider --yes --message '{prompt}'",
            "notes": "Can spawn as parallel tools to Claude Code"
        }

    @staticmethod
    def antigravity_config() -> Dict:
        """Configuration for Antigravity (automation abstraction)"""
        return {
            "tool": "antigravity",
            "description": "High-level automation and abstraction layer",
            "capabilities": [
                "Automatic dependency management",
                "Background task execution",
                "Smart caching and memoization",
                "Auto-scaling based on load",
                "Self-healing on errors"
            ],
            "integration_method": "Decorator pattern",
            "status": "conceptual",
            "notes": "Philosophy: abstract away low-level complexity"
        }
