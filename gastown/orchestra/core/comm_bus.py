"""
Agent-to-Agent Communication Bus
Handles message passing between agents
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from collections import defaultdict


class Message:
    """Represents a message between agents"""

    def __init__(self,
                 from_agent: str,
                 to_agent: str,
                 content: str,
                 message_type: str = "info",
                 metadata: Dict = None):
        self.id = str(uuid.uuid4())[:8]
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.content = content
        self.message_type = message_type  # info, task_assignment, result, error, request
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.read = False

    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "content": self.content,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "read": self.read
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create message from dictionary"""
        msg = cls(
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            content=data["content"],
            message_type=data.get("message_type", "info"),
            metadata=data.get("metadata", {})
        )
        msg.id = data["id"]
        msg.timestamp = data["timestamp"]
        msg.read = data.get("read", False)
        return msg


class CommunicationBus:
    """Manages agent-to-agent communication"""

    def __init__(self, state_dir: str = "/root/gastown/orchestra/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.messages: Dict[str, Message] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.load_state()

    def send_message(self,
                     from_agent: str,
                     to_agent: str,
                     content: str,
                     message_type: str = "info",
                     metadata: Dict = None) -> Message:
        """Send a message from one agent to another"""
        message = Message(from_agent, to_agent, content, message_type, metadata)
        self.messages[message.id] = message
        self.save_state()

        # Notify subscribers
        self._notify_subscribers(to_agent, message)

        return message

    def broadcast(self,
                  from_agent: str,
                  content: str,
                  message_type: str = "info",
                  metadata: Dict = None) -> List[Message]:
        """Broadcast a message to all agents"""
        messages = []
        # In a real system, you'd have a registry of active agents
        # For now, we'll just log the broadcast
        message = Message(from_agent, "ALL", content, message_type, metadata)
        self.messages[message.id] = message
        messages.append(message)
        self.save_state()
        return messages

    def get_messages(self,
                     agent_id: str,
                     unread_only: bool = False) -> List[Message]:
        """Get messages for an agent"""
        agent_messages = [
            msg for msg in self.messages.values()
            if msg.to_agent == agent_id or msg.to_agent == "ALL"
        ]

        if unread_only:
            agent_messages = [msg for msg in agent_messages if not msg.read]

        return sorted(agent_messages, key=lambda m: m.timestamp)

    def mark_read(self, message_id: str):
        """Mark a message as read"""
        if message_id in self.messages:
            self.messages[message_id].read = True
            self.save_state()

    def get_conversation(self, agent1: str, agent2: str) -> List[Message]:
        """Get conversation between two agents"""
        return sorted([
            msg for msg in self.messages.values()
            if (msg.from_agent == agent1 and msg.to_agent == agent2) or
               (msg.from_agent == agent2 and msg.to_agent == agent1)
        ], key=lambda m: m.timestamp)

    def get_all_messages(self) -> List[Message]:
        """Get all messages"""
        return sorted(self.messages.values(), key=lambda m: m.timestamp, reverse=True)

    def subscribe(self, agent_id: str, callback: Callable):
        """Subscribe to messages for an agent"""
        self.subscribers[agent_id].append(callback)

    def _notify_subscribers(self, agent_id: str, message: Message):
        """Notify subscribers of new message"""
        for callback in self.subscribers.get(agent_id, []):
            try:
                callback(message)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")

    def get_stats(self) -> Dict:
        """Get communication statistics"""
        total = len(self.messages)
        unread = len([m for m in self.messages.values() if not m.read])

        by_type = defaultdict(int)
        for msg in self.messages.values():
            by_type[msg.message_type] += 1

        # Agent activity
        agent_activity = defaultdict(lambda: {"sent": 0, "received": 0})
        for msg in self.messages.values():
            agent_activity[msg.from_agent]["sent"] += 1
            if msg.to_agent != "ALL":
                agent_activity[msg.to_agent]["received"] += 1

        return {
            "total_messages": total,
            "unread_messages": unread,
            "by_type": dict(by_type),
            "agent_activity": dict(agent_activity)
        }

    def save_state(self):
        """Save messages to disk"""
        state_file = self.state_dir / "messages.json"
        data = {
            msg_id: msg.to_dict()
            for msg_id, msg in self.messages.items()
        }
        state_file.write_text(json.dumps(data, indent=2))

    def load_state(self):
        """Load messages from disk"""
        state_file = self.state_dir / "messages.json"
        if state_file.exists():
            data = json.loads(state_file.read_text())
            self.messages = {
                msg_id: Message.from_dict(msg_data)
                for msg_id, msg_data in data.items()
            }

    def clear_old_messages(self, days: int = 7):
        """Clear messages older than specified days"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        to_delete = [
            msg_id for msg_id, msg in self.messages.items()
            if datetime.fromisoformat(msg.timestamp) < cutoff
        ]

        for msg_id in to_delete:
            del self.messages[msg_id]

        self.save_state()
        return len(to_delete)
