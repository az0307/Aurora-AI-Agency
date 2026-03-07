"""
Town Manager - Main Orchestration System
Coordinates agents, tasks, communication, and execution.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.task_manager import TaskManager, TaskPriority, TaskStatus
from core.comm_bus import CommunicationBus
from core.executor import TaskExecutor
from core.git_state import GitStateManager
from agents.base_agent import (
    BaseAgent, MayorAgent, WorkerAgent, SpecialistAgent, MonitorAgent,
    AgentStatus, ThinkingMethod
)


class TownManager:
    """
    Main orchestration system that manages the entire "town".
    Now with real AI execution, git-backed state, and live MCP.
    """

    def __init__(self, state_dir: str = None):
        base = Path(__file__).parent.parent
        self.state_dir = Path(state_dir) if state_dir else base / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Core systems
        self.task_manager = TaskManager(str(self.state_dir))
        self.comm_bus = CommunicationBus(str(self.state_dir))
        self.executor = TaskExecutor(str(base.parent.parent))
        self.git_state = GitStateManager(str(self.state_dir))

        # Register execution callback
        self.executor.on_complete.append(self._on_execution_complete)

        # Agents
        self.agents: Dict[str, BaseAgent] = {}
        self.mayor: Optional[MayorAgent] = None

        # Stats
        self.started_at = datetime.now().isoformat()

        # Initialize
        self._initialize_town()

    def _initialize_town(self):
        """Initialize the town with default agents"""
        self.mayor = MayorAgent()
        self.agents[self.mayor.id] = self.mayor

        workers = [
            WorkerAgent("Worker-Alpha", specialty="backend"),
            WorkerAgent("Worker-Beta", specialty="frontend"),
            WorkerAgent("Worker-Gamma", specialty="testing"),
        ]
        for w in workers:
            self.agents[w.id] = w

        specialists = [
            SpecialistAgent("Specialist-Python", "Python Development"),
            SpecialistAgent("Specialist-JS", "JavaScript/React"),
            SpecialistAgent("Specialist-DevOps", "DevOps/Infrastructure"),
        ]
        for s in specialists:
            self.agents[s.id] = s

        monitor = MonitorAgent()
        self.agents[monitor.id] = monitor

        self.comm_bus.broadcast(
            from_agent=self.mayor.id,
            content="Town initialized. All agents ready.",
            message_type="info"
        )
        self.save_state()

    def create_task(self,
                    title: str,
                    description: str = "",
                    priority: str = "medium",
                    thinking_method: str = "sequential",
                    auto_assign: bool = True,
                    auto_execute: bool = False) -> Dict:
        """Create a new task. Set auto_execute=True to run it immediately."""
        task = self.task_manager.create_task(
            title=title,
            description=description,
            task_type="task",
            priority=TaskPriority(priority)
        )

        task.thinking_method = thinking_method
        task.prompt = self.mayor.generate_prompt(task.to_dict())
        self.task_manager.update_task(
            task.id, prompt=task.prompt, thinking_method=thinking_method
        )

        self.comm_bus.send_message(
            from_agent=self.mayor.id,
            to_agent="ALL",
            content=f"New task created: {title}",
            message_type="task_assignment",
            metadata={"task_id": task.id, "thinking_method": thinking_method}
        )

        assigned_ids = []
        if auto_assign:
            assigned_ids = self.assign_task(task.id)

        # Execute the task if requested and an agent was assigned
        if auto_execute and assigned_ids:
            agent_id = assigned_ids[0]
            agent = self.agents.get(agent_id)
            if agent:
                self.execute_task(task.id, agent_id)

        return task.to_dict()

    def assign_task(self, task_id: str) -> List[str]:
        """Assign a task to appropriate agent(s)"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return []

        task_dict = task.to_dict()
        available_agents = [
            a for a in self.agents.values() if a.id != self.mayor.id
        ]

        assigned_agent_ids = self.mayor.delegate_task(task_dict, available_agents)

        for agent_id in assigned_agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                self.task_manager.update_task(
                    task_id,
                    assigned_to=agent_id,
                    status=TaskStatus.IN_PROGRESS.value
                )

                agent_prompt = agent.generate_prompt(task_dict)

                self.comm_bus.send_message(
                    from_agent=self.mayor.id,
                    to_agent=agent_id,
                    content=f"Task assigned: {task.title}",
                    message_type="task_assignment",
                    metadata={"task_id": task_id, "prompt": agent_prompt}
                )

                agent.status = AgentStatus.WORKING
                agent.current_task_id = task_id

        self.save_state()
        return assigned_agent_ids

    def execute_task(self, task_id: str, agent_id: str,
                     method: str = "api") -> Dict:
        """Execute a task using the AI executor"""
        task = self.task_manager.get_task(task_id)
        agent = self.agents.get(agent_id)
        if not task or not agent:
            return {"error": "Task or agent not found"}

        prompt = task.prompt or agent.generate_prompt(task.to_dict())

        self.comm_bus.send_message(
            from_agent=self.mayor.id,
            to_agent=agent_id,
            content=f"Executing task: {task.title}",
            message_type="info",
            metadata={"task_id": task_id, "method": method}
        )

        result = self.executor.execute_task(
            task=task.to_dict(),
            agent=agent.to_dict(),
            prompt=prompt,
            method=method
        )

        return result.to_dict()

    def execute_task_async(self, task_id: str, agent_id: str,
                           method: str = "api") -> str:
        """Execute a task in the background"""
        task = self.task_manager.get_task(task_id)
        agent = self.agents.get(agent_id)
        if not task or not agent:
            return ""

        prompt = task.prompt or agent.generate_prompt(task.to_dict())

        return self.executor.execute_task_async(
            task=task.to_dict(),
            agent=agent.to_dict(),
            prompt=prompt,
            method=method
        )

    def _on_execution_complete(self, result):
        """Callback when an execution completes"""
        task_id = result.task_id
        agent_id = result.agent_id

        if result.status == "completed":
            self.complete_task(task_id, result.output, agent_id)
        elif result.status == "failed":
            task = self.task_manager.get_task(task_id)
            if task:
                self.task_manager.update_task(
                    task_id, status=TaskStatus.FAILED.value,
                    result=result.error
                )
            agent = self.agents.get(agent_id)
            if agent:
                agent.status = AgentStatus.ERROR
                agent.tasks_failed += 1

    def complete_task(self, task_id: str, result: str = None,
                      agent_id: str = None):
        """Mark a task as completed"""
        task = self.task_manager.complete_task(task_id, result)

        if task and agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task_id = None
                agent.tasks_completed += 1

                self.comm_bus.send_message(
                    from_agent=agent_id,
                    to_agent=self.mayor.id,
                    content=f"Task completed: {task.title}",
                    message_type="result",
                    metadata={"task_id": task_id, "result": result}
                )
        self.save_state()

    def create_subtasks(self, parent_task_id: str,
                        subtasks: List[Dict]) -> List[Dict]:
        """Create subtasks for a parent task"""
        created = []
        for subtask_info in subtasks:
            subtask = self.task_manager.create_task(
                title=subtask_info["title"],
                description=subtask_info.get("description", ""),
                task_type="subtask",
                priority=TaskPriority(
                    subtask_info.get("priority", "medium")
                ),
                parent_id=parent_task_id
            )

            if "thinking_method" in subtask_info:
                subtask.thinking_method = subtask_info["thinking_method"]

            agent_type = subtask_info.get("agent_type", "worker")
            if agent_type == "specialist":
                agent = SpecialistAgent(
                    "temp", specialty=subtask_info.get("specialty", "general")
                )
            else:
                agent = WorkerAgent(
                    "temp", specialty=subtask_info.get("specialty")
                )

            subtask.prompt = agent.generate_prompt(subtask.to_dict())
            self.task_manager.update_task(subtask.id, prompt=subtask.prompt)
            created.append(subtask.to_dict())

        return created

    def get_town_status(self) -> Dict:
        return {
            "started_at": self.started_at,
            "agents": {
                "total": len(self.agents),
                "by_status": self._get_agent_stats_by_status(),
                "list": [agent.to_dict() for agent in self.agents.values()]
            },
            "tasks": self.task_manager.get_stats(),
            "communication": self.comm_bus.get_stats(),
            "execution": self.executor.get_stats(),
            "mayor": self.mayor.to_dict() if self.mayor else None
        }

    def _get_agent_stats_by_status(self) -> Dict:
        stats = {}
        for status in AgentStatus:
            stats[status.value] = len([
                a for a in self.agents.values() if a.status == status
            ])
        return stats

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        agent = self.agents.get(agent_id)
        return agent.to_dict() if agent else None

    def get_all_agents(self) -> List[Dict]:
        return [agent.to_dict() for agent in self.agents.values()]

    def get_task_with_hierarchy(self, task_id: str) -> Dict:
        return self.task_manager.get_task_hierarchy(task_id)

    def get_all_tasks(self) -> List[Dict]:
        return [task.to_dict() for task in self.task_manager.get_all_tasks()]

    def get_messages(self, agent_id: str = None,
                     unread_only: bool = False) -> List[Dict]:
        if agent_id:
            messages = self.comm_bus.get_messages(agent_id, unread_only)
        else:
            messages = self.comm_bus.get_all_messages()
        return [msg.to_dict() for msg in messages]

    def send_message(self, from_agent: str, to_agent: str,
                     content: str, message_type: str = "info") -> Dict:
        msg = self.comm_bus.send_message(
            from_agent, to_agent, content, message_type
        )
        return msg.to_dict()

    def save_state(self):
        state_file = self.state_dir / "town.json"
        state = {
            "started_at": self.started_at,
            "agents": {
                aid: agent.to_dict()
                for aid, agent in self.agents.items()
            },
            "mayor_id": self.mayor.id if self.mayor else None
        }
        state_file.write_text(json.dumps(state, indent=2))

    def load_state(self):
        state_file = self.state_dir / "town.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            self.started_at = state.get(
                "started_at", datetime.now().isoformat()
            )
