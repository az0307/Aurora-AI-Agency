"""
Town Manager - Main Orchestration System
Coordinates agents, tasks, and communication
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import sys
sys.path.append('/root/gastown/orchestra')

from tasks.task_manager import TaskManager, TaskPriority, TaskStatus
from core.comm_bus import CommunicationBus
from agents.base_agent import (
    BaseAgent, MayorAgent, WorkerAgent, SpecialistAgent, MonitorAgent,
    AgentStatus, ThinkingMethod
)


class TownManager:
    """
    Main orchestration system that manages the entire "town"
    """

    def __init__(self, state_dir: str = "/root/gastown/orchestra/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Core systems
        self.task_manager = TaskManager(state_dir)
        self.comm_bus = CommunicationBus(state_dir)

        # Agents
        self.agents: Dict[str, BaseAgent] = {}
        self.mayor: Optional[MayorAgent] = None

        # Stats
        self.started_at = datetime.now().isoformat()

        # Initialize
        self._initialize_town()

    def _initialize_town(self):
        """Initialize the town with default agents"""
        # Create Mayor
        self.mayor = MayorAgent()
        self.agents[self.mayor.id] = self.mayor

        # Create some default workers
        worker1 = WorkerAgent("Worker-Alpha", specialty="backend")
        worker2 = WorkerAgent("Worker-Beta", specialty="frontend")
        worker3 = WorkerAgent("Worker-Gamma", specialty="testing")

        self.agents[worker1.id] = worker1
        self.agents[worker2.id] = worker2
        self.agents[worker3.id] = worker3

        # Create specialists
        specialist1 = SpecialistAgent("Specialist-Python", "Python Development")
        specialist2 = SpecialistAgent("Specialist-JS", "JavaScript/React")
        specialist3 = SpecialistAgent("Specialist-DevOps", "DevOps/Infrastructure")

        self.agents[specialist1.id] = specialist1
        self.agents[specialist2.id] = specialist2
        self.agents[specialist3.id] = specialist3

        # Create monitor
        monitor = MonitorAgent()
        self.agents[monitor.id] = monitor

        # Mayor broadcasts initialization
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
                    auto_assign: bool = True) -> Dict:
        """
        Create a new task
        This is the main entry point for user task creation
        """
        task = self.task_manager.create_task(
            title=title,
            description=description,
            task_type="task",
            priority=TaskPriority(priority)
        )

        # Set thinking method
        task.thinking_method = thinking_method
        task.prompt = self.mayor.generate_prompt(task.to_dict())
        self.task_manager.update_task(task.id, prompt=task.prompt, thinking_method=thinking_method)

        # Mayor announces new task
        self.comm_bus.send_message(
            from_agent=self.mayor.id,
            to_agent="ALL",
            content=f"New task created: {title}",
            message_type="task_assignment",
            metadata={"task_id": task.id, "thinking_method": thinking_method}
        )

        # Auto-assign if requested
        if auto_assign:
            self.assign_task(task.id)

        return task.to_dict()

    def assign_task(self, task_id: str) -> List[str]:
        """
        Assign a task to appropriate agent(s)
        Mayor decides which agents to assign based on thinking method
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return []

        task_dict = task.to_dict()
        available_agents = [a for a in self.agents.values() if a.id != self.mayor.id]

        # Mayor delegates
        assigned_agent_ids = self.mayor.delegate_task(task_dict, available_agents)

        # Assign and notify
        for agent_id in assigned_agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                self.task_manager.update_task(
                    task_id,
                    assigned_to=agent_id,
                    status=TaskStatus.IN_PROGRESS.value
                )

                # Generate agent-specific prompt
                agent_prompt = agent.generate_prompt(task_dict)

                # Mayor sends assignment message
                self.comm_bus.send_message(
                    from_agent=self.mayor.id,
                    to_agent=agent_id,
                    content=f"Task assigned: {task.title}",
                    message_type="task_assignment",
                    metadata={
                        "task_id": task_id,
                        "prompt": agent_prompt
                    }
                )

                # Update agent status
                agent.status = AgentStatus.WORKING
                agent.current_task_id = task_id

        self.save_state()
        return assigned_agent_ids

    def complete_task(self, task_id: str, result: str = None, agent_id: str = None):
        """Mark a task as completed"""
        task = self.task_manager.complete_task(task_id, result)

        if task and agent_id:
            agent = self.agents.get(agent_id)
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task_id = None
                agent.tasks_completed += 1

                # Agent reports completion to Mayor
                self.comm_bus.send_message(
                    from_agent=agent_id,
                    to_agent=self.mayor.id,
                    content=f"Task completed: {task.title}",
                    message_type="result",
                    metadata={"task_id": task_id, "result": result}
                )

        self.save_state()

    def create_subtasks(self, parent_task_id: str, subtasks: List[Dict]) -> List[Dict]:
        """Create subtasks for a parent task"""
        created = []
        for subtask_info in subtasks:
            subtask = self.task_manager.create_task(
                title=subtask_info["title"],
                description=subtask_info.get("description", ""),
                task_type="subtask",
                priority=TaskPriority(subtask_info.get("priority", "medium")),
                parent_id=parent_task_id
            )

            # Set thinking method if specified
            if "thinking_method" in subtask_info:
                subtask.thinking_method = subtask_info["thinking_method"]

            # Generate prompt
            agent_type = subtask_info.get("agent_type", "worker")
            if agent_type == "worker":
                agent = WorkerAgent("temp", specialty=subtask_info.get("specialty"))
            elif agent_type == "specialist":
                agent = SpecialistAgent("temp", specialty=subtask_info.get("specialty", "general"))
            else:
                agent = WorkerAgent("temp")

            subtask.prompt = agent.generate_prompt(subtask.to_dict())
            self.task_manager.update_task(subtask.id, prompt=subtask.prompt)

            created.append(subtask.to_dict())

        return created

    def get_town_status(self) -> Dict:
        """Get overall town status"""
        return {
            "started_at": self.started_at,
            "agents": {
                "total": len(self.agents),
                "by_status": self._get_agent_stats_by_status(),
                "list": [agent.to_dict() for agent in self.agents.values()]
            },
            "tasks": self.task_manager.get_stats(),
            "communication": self.comm_bus.get_stats(),
            "mayor": self.mayor.to_dict() if self.mayor else None
        }

    def _get_agent_stats_by_status(self) -> Dict:
        """Get agent count by status"""
        stats = {}
        for status in AgentStatus:
            stats[status.value] = len([
                a for a in self.agents.values()
                if a.status == status
            ])
        return stats

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent info"""
        agent = self.agents.get(agent_id)
        return agent.to_dict() if agent else None

    def get_all_agents(self) -> List[Dict]:
        """Get all agents"""
        return [agent.to_dict() for agent in self.agents.values()]

    def get_task_with_hierarchy(self, task_id: str) -> Dict:
        """Get task with full hierarchy"""
        return self.task_manager.get_task_hierarchy(task_id)

    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return [task.to_dict() for task in self.task_manager.get_all_tasks()]

    def get_messages(self, agent_id: str = None, unread_only: bool = False) -> List[Dict]:
        """Get messages"""
        if agent_id:
            messages = self.comm_bus.get_messages(agent_id, unread_only)
        else:
            messages = self.comm_bus.get_all_messages()
        return [msg.to_dict() for msg in messages]

    def send_message(self, from_agent: str, to_agent: str, content: str, message_type: str = "info") -> Dict:
        """Send a message"""
        msg = self.comm_bus.send_message(from_agent, to_agent, content, message_type)
        return msg.to_dict()

    def save_state(self):
        """Save town state"""
        state_file = self.state_dir / "town.json"
        state = {
            "started_at": self.started_at,
            "agents": {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()},
            "mayor_id": self.mayor.id if self.mayor else None
        }
        state_file.write_text(json.dumps(state, indent=2))

    def load_state(self):
        """Load town state"""
        state_file = self.state_dir / "town.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            self.started_at = state.get("started_at", datetime.now().isoformat())
            # Note: Full agent restoration would require more complex deserialization
            # For now, we reinitialize on startup
