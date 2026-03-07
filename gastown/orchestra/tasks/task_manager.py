"""
Hierarchical Task Management System
Tracks tasks → implementation steps → subtasks
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import List, Dict, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task:
    """Represents a task in the hierarchy"""

    def __init__(self,
                 title: str,
                 description: str = "",
                 task_type: str = "task",
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 parent_id: Optional[str] = None):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.task_type = task_type  # task, implementation, subtask
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.parent_id = parent_id
        self.assigned_to = None  # Agent ID
        self.children: List[str] = []  # Child task IDs
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.completed_at = None
        self.metadata = {}
        self.prompt = None  # Generated prompt for this task
        self.thinking_method = None  # swarm, parallel, twin
        self.result = None

    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "assigned_to": self.assigned_to,
            "children": self.children,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
            "prompt": self.prompt,
            "thinking_method": self.thinking_method,
            "result": self.result
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            task_type=data.get("task_type", "task"),
            priority=TaskPriority(data.get("priority", "medium"))
        )
        task.id = data["id"]
        task.status = TaskStatus(data["status"])
        task.parent_id = data.get("parent_id")
        task.assigned_to = data.get("assigned_to")
        task.children = data.get("children", [])
        task.created_at = data.get("created_at")
        task.updated_at = data.get("updated_at")
        task.completed_at = data.get("completed_at")
        task.metadata = data.get("metadata", {})
        task.prompt = data.get("prompt")
        task.thinking_method = data.get("thinking_method")
        task.result = data.get("result")
        return task


class TaskManager:
    """Manages hierarchical task structure"""

    def __init__(self, state_dir: str = None):
        base = Path(__file__).parent.parent
        self.state_dir = Path(state_dir) if state_dir else base / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, Task] = {}
        self.load_state()

    def create_task(self,
                    title: str,
                    description: str = "",
                    task_type: str = "task",
                    priority: TaskPriority = TaskPriority.MEDIUM,
                    parent_id: Optional[str] = None) -> Task:
        """Create a new task"""
        task = Task(title, description, task_type, priority, parent_id)
        self.tasks[task.id] = task

        # Add to parent's children if parent exists
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].children.append(task.id)
            self.tasks[parent_id].updated_at = datetime.now().isoformat()

        self.save_state()
        return task

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """Update a task"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                if key == "status" and isinstance(value, str):
                    task.status = TaskStatus(value)
                elif key == "priority" and isinstance(value, str):
                    task.priority = TaskPriority(value)
                else:
                    setattr(task, key, value)

        task.updated_at = datetime.now().isoformat()

        if task.status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.now().isoformat()

        self.save_state()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        return [t for t in self.tasks.values() if t.status == status]

    def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """Get tasks assigned to an agent"""
        return [t for t in self.tasks.values() if t.assigned_to == agent_id]

    def get_children(self, task_id: str) -> List[Task]:
        """Get child tasks"""
        task = self.get_task(task_id)
        if not task:
            return []
        return [self.tasks[child_id] for child_id in task.children if child_id in self.tasks]

    def get_task_hierarchy(self, task_id: str) -> Dict:
        """Get task with full hierarchy"""
        task = self.get_task(task_id)
        if not task:
            return {}

        task_dict = task.to_dict()
        task_dict["children"] = [
            self.get_task_hierarchy(child_id)
            for child_id in task.children
        ]
        return task_dict

    def get_root_tasks(self) -> List[Task]:
        """Get all root tasks (no parent)"""
        return [t for t in self.tasks.values() if not t.parent_id]

    def assign_task(self, task_id: str, agent_id: str) -> Optional[Task]:
        """Assign a task to an agent"""
        return self.update_task(task_id, assigned_to=agent_id)

    def complete_task(self, task_id: str, result: str = None) -> Optional[Task]:
        """Mark a task as completed"""
        return self.update_task(
            task_id,
            status=TaskStatus.COMPLETED.value,
            result=result
        )

    def delete_task(self, task_id: str) -> bool:
        """Delete a task and its children"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Delete children first
        for child_id in task.children[:]:
            self.delete_task(child_id)

        # Remove from parent's children
        if task.parent_id and task.parent_id in self.tasks:
            parent = self.tasks[task.parent_id]
            if task_id in parent.children:
                parent.children.remove(task_id)

        # Delete the task
        del self.tasks[task_id]
        self.save_state()
        return True

    def save_state(self):
        """Save tasks to disk"""
        state_file = self.state_dir / "tasks.json"
        data = {
            task_id: task.to_dict()
            for task_id, task in self.tasks.items()
        }
        state_file.write_text(json.dumps(data, indent=2))

    def load_state(self):
        """Load tasks from disk"""
        state_file = self.state_dir / "tasks.json"
        if state_file.exists():
            data = json.loads(state_file.read_text())
            self.tasks = {
                task_id: Task.from_dict(task_data)
                for task_id, task_data in data.items()
            }

    def get_stats(self) -> Dict:
        """Get task statistics"""
        total = len(self.tasks)
        by_status = {}
        for status in TaskStatus:
            by_status[status.value] = len(self.get_tasks_by_status(status))

        by_type = {}
        for task in self.tasks.values():
            by_type[task.task_type] = by_type.get(task.task_type, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type,
            "root_tasks": len(self.get_root_tasks())
        }
