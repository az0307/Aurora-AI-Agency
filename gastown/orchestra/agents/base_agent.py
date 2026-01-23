"""
Base Agent Class and Agent Types
Supports different thinking methods: swarm, parallel, twin
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class AgentRole(Enum):
    MAYOR = "mayor"  # Main orchestrator
    WORKER = "worker"  # General worker
    SPECIALIST = "specialist"  # Specialized task handler
    MONITOR = "monitor"  # System monitor


class ThinkingMethod(Enum):
    SEQUENTIAL = "sequential"  # Traditional one-step-at-a-time
    SWARM = "swarm"  # Multiple agents collaborate
    PARALLEL = "parallel"  # Run multiple approaches simultaneously
    TWIN = "twin"  # Two agents cross-check each other


class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class BaseAgent:
    """Base class for all agents"""

    def __init__(self,
                 name: str,
                 role: AgentRole = AgentRole.WORKER,
                 specialty: str = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.specialty = specialty
        self.status = AgentStatus.IDLE
        self.current_task_id = None
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert agent to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "specialty": self.specialty,
            "status": self.status.value,
            "current_task_id": self.current_task_id,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "metadata": self.metadata
        }

    def generate_prompt(self, task: Dict) -> str:
        """Generate optimized prompt for a task"""
        raise NotImplementedError("Subclasses must implement generate_prompt")

    def execute_task(self, task: Dict) -> Dict:
        """Execute a task"""
        raise NotImplementedError("Subclasses must implement execute_task")


class MayorAgent(BaseAgent):
    """
    Mayor Agent - Main orchestrator that delegates tasks
    """

    def __init__(self):
        super().__init__(name="Mayor", role=AgentRole.MAYOR)
        self.active_agents: List[str] = []

    def generate_prompt(self, task: Dict) -> str:
        """Generate optimized prompt for task delegation"""
        thinking_method = task.get("thinking_method", "sequential")

        base_prompt = f"""Task: {task['title']}
Description: {task.get('description', '')}

Thinking Method: {thinking_method}
"""

        if thinking_method == ThinkingMethod.SWARM.value:
            base_prompt += """
Approach: Deploy multiple specialized agents to collaborate on this task.
- Break down into subtasks
- Assign to appropriate specialists
- Coordinate their efforts
- Synthesize results
"""
        elif thinking_method == ThinkingMethod.PARALLEL.value:
            base_prompt += """
Approach: Run multiple solution strategies in parallel.
- Identify 2-3 different approaches
- Execute simultaneously
- Compare results
- Select best solution
"""
        elif thinking_method == ThinkingMethod.TWIN.value:
            base_prompt += """
Approach: Use twin agents for verification.
- Agent A implements solution
- Agent B independently verifies
- Cross-check results
- Resolve discrepancies
"""

        deliverables = task.get('deliverables', '- Complete implementation\n- Test results\n- Documentation')
        base_prompt += f"""
Priority: {task.get('priority', 'medium')}

Expected Deliverables:
{deliverables}
"""
        return base_prompt

    def execute_task(self, task: Dict) -> Dict:
        """Mayor doesn't execute tasks, it delegates"""
        return {
            "status": "delegated",
            "message": "Task delegated to appropriate agents"
        }

    def delegate_task(self, task: Dict, agents: List[BaseAgent]) -> List[str]:
        """Delegate task to appropriate agents"""
        thinking_method = task.get("thinking_method", ThinkingMethod.SEQUENTIAL.value)
        assigned_agents = []

        if thinking_method == ThinkingMethod.SWARM.value:
            # Assign to multiple specialists
            specialists = [a for a in agents if a.role == AgentRole.SPECIALIST]
            assigned_agents = [a.id for a in specialists[:3]]

        elif thinking_method == ThinkingMethod.PARALLEL.value:
            # Assign to multiple workers for parallel execution
            workers = [a for a in agents if a.status == AgentStatus.IDLE]
            assigned_agents = [a.id for a in workers[:2]]

        elif thinking_method == ThinkingMethod.TWIN.value:
            # Assign to two workers for twin verification
            workers = [a for a in agents if a.status == AgentStatus.IDLE]
            assigned_agents = [a.id for a in workers[:2]]

        else:
            # Sequential - assign to single best agent
            available = [a for a in agents if a.status == AgentStatus.IDLE]
            if available:
                assigned_agents = [available[0].id]

        return assigned_agents


class WorkerAgent(BaseAgent):
    """
    Worker Agent - Executes tasks
    """

    def __init__(self, name: str, specialty: str = None):
        super().__init__(name=name, role=AgentRole.WORKER, specialty=specialty)

    def generate_prompt(self, task: Dict) -> str:
        """Generate optimized execution prompt"""
        prompt = f"""Execute Task: {task['title']}

Objective: {task.get('description', '')}

Instructions:
1. Analyze the requirements carefully
2. Break down into implementation steps
3. Execute each step methodically
4. Test thoroughly
5. Document your work

"""
        if self.specialty:
            prompt += f"Apply your expertise in {self.specialty} to this task.\n"

        context = task.get('context', 'No additional context provided')
        success_criteria = task.get('success_criteria', '- Task completed successfully\n- All tests pass\n- Code is clean and documented')
        prompt += f"""
Context:
{context}

Success Criteria:
{success_criteria}
"""
        return prompt

    def execute_task(self, task: Dict) -> Dict:
        """Execute the task (stub - would call Claude Code in real implementation)"""
        self.status = AgentStatus.WORKING
        self.current_task_id = task.get('id')
        self.last_active = datetime.now().isoformat()

        # In real implementation, this would spawn a Claude Code instance
        # and execute the task

        return {
            "status": "in_progress",
            "agent_id": self.id,
            "task_id": task.get('id'),
            "prompt": self.generate_prompt(task)
        }


class SpecialistAgent(BaseAgent):
    """
    Specialist Agent - Expert in specific domain
    """

    def __init__(self, name: str, specialty: str):
        super().__init__(name=name, role=AgentRole.SPECIALIST, specialty=specialty)
        self.expertise_areas = []

    def generate_prompt(self, task: Dict) -> str:
        """Generate specialist-optimized prompt"""
        prompt = f"""[SPECIALIST: {self.specialty}] Task: {task['title']}

Leveraging expertise in: {self.specialty}

Task Description: {task.get('description', '')}

Expert Approach:
1. Apply {self.specialty} best practices
2. Use domain-specific patterns and techniques
3. Ensure quality standards for {self.specialty}
4. Optimize for {self.specialty} performance

"""
        if self.expertise_areas:
            prompt += f"Focus areas: {', '.join(self.expertise_areas)}\n\n"

        default_criteria = f'- Meets {self.specialty} standards\n- Best practices followed\n- Optimized implementation'
        success_criteria = task.get('success_criteria', default_criteria)
        prompt += f"""Success Metrics:
{success_criteria}
"""
        return prompt

    def execute_task(self, task: Dict) -> Dict:
        """Execute specialized task"""
        self.status = AgentStatus.WORKING
        self.current_task_id = task.get('id')
        self.last_active = datetime.now().isoformat()

        return {
            "status": "in_progress",
            "agent_id": self.id,
            "specialty": self.specialty,
            "task_id": task.get('id'),
            "prompt": self.generate_prompt(task)
        }


class MonitorAgent(BaseAgent):
    """
    Monitor Agent - Watches system health and reports
    """

    def __init__(self):
        super().__init__(name="Monitor", role=AgentRole.MONITOR)

    def generate_prompt(self, task: Dict) -> str:
        """Generate monitoring prompt"""
        return f"""[MONITOR] System Health Check

Monitor: {task.get('description', 'General system monitoring')}

Check:
- Agent status and health
- Task completion rates
- Error rates
- Resource usage
- Communication flow

Report any anomalies or issues requiring attention.
"""

    def execute_task(self, task: Dict) -> Dict:
        """Execute monitoring task"""
        return {
            "status": "monitoring",
            "agent_id": self.id,
            "task_id": task.get('id')
        }
