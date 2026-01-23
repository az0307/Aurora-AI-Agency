"""
Enhanced Mayor with Teams and Thinking Visibility
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import sys
sys.path.append('/root/gastown/orchestra')

from agents.base_agent import MayorAgent
from agents.teams import (
    Team, TeamType, AdvisorAgent, UtilityAgent, PromptingAgent,
    IntegrationPoint
)


class EnhancedMayor(MayorAgent):
    """
    Enhanced Mayor with team management and visible thinking
    """

    def __init__(self):
        super().__init__()
        self.teams: Dict[str, Team] = {}
        self.advisors: Dict[str, AdvisorAgent] = {}
        self.utilities: Dict[str, UtilityAgent] = {}
        self.prompters: Dict[str, PromptingAgent] = {}

        self.current_thinking: List[str] = []
        self.decisions: List[Dict] = []
        self.integration_points = {
            "claude_code": IntegrationPoint.claude_code_config(),
            "opencode": IntegrationPoint.opencode_config(),
            "antigravity": IntegrationPoint.antigravity_config()
        }

        self._initialize_teams()

    def _initialize_teams(self):
        """Initialize Mayor's teams"""
        # Create Advisor Team
        advisor_team = Team("Strategic Advisors", TeamType.ADVISOR)
        self.teams[advisor_team.id] = advisor_team

        # Add advisors
        advisors = [
            AdvisorAgent("Advisor-Planning", "planning"),
            AdvisorAgent("Advisor-Architecture", "architecture"),
            AdvisorAgent("Advisor-Optimization", "optimization"),
            AdvisorAgent("Advisor-Risk", "risk")
        ]

        for advisor in advisors:
            self.advisors[advisor.id] = advisor
            advisor_team.members.append(advisor.id)

        # Create Utility Team
        utility_team = Team("Utility Tools", TeamType.UTILITY)
        self.teams[utility_team.id] = utility_team

        # Add utilities
        utilities = [
            UtilityAgent("Utility-WebSearch", "web_search"),
            UtilityAgent("Utility-DeepThink", "deep_think"),
            UtilityAgent("Utility-Browser", "browser"),
            UtilityAgent("Utility-ComputerUse", "computer_use")
        ]

        for utility in utilities:
            self.utilities[utility.id] = utility
            utility_team.members.append(utility.id)

        # Create Prompting Team
        prompting_team = Team("Prompt Engineers", TeamType.PROMPTING)
        self.teams[prompting_team.id] = prompting_team

        # Add prompters
        prompters = [
            PromptingAgent("Prompter-ChainOfThought", "chain_of_thought"),
            PromptingAgent("Prompter-FewShot", "few_shot"),
            PromptingAgent("Prompter-TreeOfThought", "tree_of_thought"),
            PromptingAgent("Prompter-ZeroShot", "zero_shot")
        ]

        for prompter in prompters:
            self.prompters[prompter.id] = prompter
            prompting_team.members.append(prompter.id)

    def think(self, task: Dict, context: Dict = None) -> Dict:
        """
        Enhanced thinking with visibility
        Returns the Mayor's thought process
        """
        self.current_thinking = []
        thinking_process = {
            "task_id": task.get("id"),
            "task_title": task.get("title"),
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }

        # Step 1: Analyze task
        self._think("📋 Analyzing task: " + task.get("title"))
        thinking_process["steps"].append({
            "step": 1,
            "action": "analyze_task",
            "thought": f"Task priority: {task.get('priority')}, Thinking method: {task.get('thinking_method')}"
        })

        # Step 2: Consult advisors
        self._think("🎯 Consulting advisor team...")
        advisor_insights = self._consult_advisors(task)
        thinking_process["steps"].append({
            "step": 2,
            "action": "consult_advisors",
            "insights": advisor_insights
        })

        # Step 3: Determine utility needs
        self._think("🔧 Checking utility requirements...")
        utility_needs = self._determine_utilities(task)
        thinking_process["steps"].append({
            "step": 3,
            "action": "determine_utilities",
            "utilities": utility_needs
        })

        # Step 4: Generate optimized prompt
        self._think("✍️ Generating optimized prompt...")
        enhanced_prompt = self._get_enhanced_prompt(task)
        thinking_process["steps"].append({
            "step": 4,
            "action": "generate_prompt",
            "prompt_method": enhanced_prompt["method"]
        })

        # Step 5: Plan delegation
        self._think("👥 Planning agent delegation...")
        delegation_plan = self._plan_delegation(task, advisor_insights)
        thinking_process["steps"].append({
            "step": 5,
            "action": "plan_delegation",
            "plan": delegation_plan
        })

        # Step 6: Decision
        self._think("✅ Decision made")
        decision = {
            "task_id": task.get("id"),
            "delegation": delegation_plan,
            "prompt": enhanced_prompt,
            "utilities": utility_needs,
            "advisor_recommendations": advisor_insights,
            "timestamp": datetime.now().isoformat()
        }

        self.decisions.append(decision)
        thinking_process["final_decision"] = decision
        thinking_process["thinking_log"] = self.current_thinking.copy()

        return thinking_process

    def _think(self, thought: str):
        """Record a thought"""
        self.current_thinking.append({
            "timestamp": datetime.now().isoformat(),
            "thought": thought
        })

    def _consult_advisors(self, task: Dict) -> List[Dict]:
        """Consult all advisors for insights"""
        insights = []
        for advisor in self.advisors.values():
            advice = advisor.analyze_task(task)
            insights.append(advice)
        return insights

    def _determine_utilities(self, task: Dict) -> List[Dict]:
        """Determine which utilities might be needed"""
        utilities_needed = []
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()

        # Check for web search needs
        if any(word in title + description for word in ["documentation", "best practices", "examples", "research"]):
            utilities_needed.append({
                "utility": "web_search",
                "reason": "Task may benefit from researching documentation or examples"
            })

        # Check for deep thinking needs
        if task.get("priority") in ["high", "critical"] or task.get("thinking_method") in ["swarm", "twin"]:
            utilities_needed.append({
                "utility": "deep_think",
                "reason": "Complex task requiring extended reasoning"
            })

        # Check for browser needs
        if any(word in title + description for word in ["web", "scrape", "download", "browse", "website"]):
            utilities_needed.append({
                "utility": "browser",
                "reason": "Task involves web interaction"
            })

        # Check for computer use needs
        if any(word in title + description for word in ["system", "install", "configure", "desktop", "gui"]):
            utilities_needed.append({
                "utility": "computer_use",
                "reason": "Task requires system-level operations"
            })

        return utilities_needed

    def _get_enhanced_prompt(self, task: Dict) -> Dict:
        """Get enhanced prompt from prompting team"""
        thinking_method = task.get("thinking_method", "sequential")

        # Select appropriate prompter based on task complexity
        if task.get("priority") in ["high", "critical"]:
            prompter = self.prompters.get(
                [p for p in self.prompters.values() if p.specialty == "tree_of_thought"][0].id
            )
            if not prompter:
                prompter = list(self.prompters.values())[0]
        else:
            prompter = list(self.prompters.values())[0]

        enhanced_prompt = prompter.generate_enhanced_prompt(task, thinking_method)

        return {
            "method": prompter.specialty,
            "prompter_id": prompter.id,
            "prompt": enhanced_prompt
        }

    def _plan_delegation(self, task: Dict, advisor_insights: List[Dict]) -> Dict:
        """Plan how to delegate this task"""
        thinking_method = task.get("thinking_method", "sequential")
        priority = task.get("priority", "medium")

        plan = {
            "thinking_method": thinking_method,
            "priority": priority,
            "recommended_agents": [],
            "team_assignment": None,
            "reasoning": []
        }

        # Analyze advisor recommendations
        for insight in advisor_insights:
            if insight["specialty"] == "risk" and priority in ["high", "critical"]:
                plan["reasoning"].append("High priority task - recommend twin validation or swarm approach")

        # Determine delegation strategy
        if thinking_method == "swarm":
            plan["team_assignment"] = "execution_team"
            plan["recommended_agents"] = ["multiple_specialists"]
            plan["reasoning"].append("Swarm method: Deploy team of specialists")

        elif thinking_method == "parallel":
            plan["team_assignment"] = "execution_team"
            plan["recommended_agents"] = ["multiple_workers"]
            plan["reasoning"].append("Parallel method: Deploy multiple workers with different approaches")

        elif thinking_method == "twin":
            plan["team_assignment"] = "execution_team"
            plan["recommended_agents"] = ["two_agents"]
            plan["reasoning"].append("Twin method: Deploy two agents for cross-verification")

        else:
            plan["team_assignment"] = "single_agent"
            plan["recommended_agents"] = ["best_available"]
            plan["reasoning"].append("Sequential method: Single best-fit agent")

        return plan

    def get_current_thinking(self) -> List[str]:
        """Get Mayor's current thinking process"""
        return self.current_thinking

    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent Mayor decisions"""
        return self.decisions[-limit:]

    def to_dict(self) -> Dict:
        """Enhanced dict representation"""
        base = super().to_dict()
        base["teams"] = {team_id: team.to_dict() for team_id, team in self.teams.items()}
        base["advisors"] = {adv_id: adv.to_dict() for adv_id, adv in self.advisors.items()}
        base["utilities"] = {util_id: util.to_dict() for util_id, util in self.utilities.items()}
        base["prompters"] = {prom_id: prom.to_dict() for prom_id, prom in self.prompters.items()}
        base["current_thinking"] = self.current_thinking
        base["recent_decisions"] = self.get_recent_decisions(5)
        base["integration_points"] = self.integration_points
        return base
