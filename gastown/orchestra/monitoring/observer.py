"""
Observation and Monitoring System
Real-time tracking of agent behavior, system health, and performance
"""

import json
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum


class EventType(Enum):
    """Types of observable events"""
    TASK_CREATED = "task_created"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    AGENT_IDLE = "agent_idle"
    AGENT_WORKING = "agent_working"
    AGENT_ERROR = "agent_error"
    MESSAGE_SENT = "message_sent"
    MAYOR_THINKING = "mayor_thinking"
    UTILITY_CALLED = "utility_called"
    CONTEXT_COMPRESSED = "context_compressed"
    BIAS_DETECTED = "bias_detected"
    QUALITY_LOW = "quality_low"


class Event:
    """Represents an observable event"""

    def __init__(self, event_type: EventType, data: Dict, source: str = None):
        self.id = f"evt_{datetime.now().timestamp()}"
        self.type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }


class MetricCollector:
    """Collects and aggregates metrics"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))

    def record(self, metric_name: str, value: float):
        """Record a metric value"""
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

    def get_stats(self, metric_name: str) -> Dict:
        """Get statistics for a metric"""
        if metric_name not in self.metrics:
            return {}

        values = [m["value"] for m in self.metrics[metric_name]]
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None
        }

    def get_all_stats(self) -> Dict:
        """Get all metric statistics"""
        return {
            name: self.get_stats(name)
            for name in self.metrics.keys()
        }


class PerformanceMonitor:
    """Monitor system and agent performance"""

    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = MetricCollector()
        self.alerts: List[Dict] = []

    def record_task_time(self, task_id: str, duration_seconds: float):
        """Record task completion time"""
        self.metrics.record("task_duration", duration_seconds)

        # Alert if task took too long (> 5 minutes)
        if duration_seconds > 300:
            self.alerts.append({
                "timestamp": datetime.now().isoformat(),
                "severity": "warning",
                "message": f"Task {task_id} took {duration_seconds}s (> 5 min)",
                "type": "performance"
            })

    def record_agent_utilization(self, agent_id: str, utilization: float):
        """Record agent utilization (0-100%)"""
        self.metrics.record(f"agent_{agent_id}_utilization", utilization)

        # Alert if agent is overutilized
        if utilization > 90:
            self.alerts.append({
                "timestamp": datetime.now().isoformat(),
                "severity": "warning",
                "message": f"Agent {agent_id} is {utilization}% utilized",
                "type": "capacity"
            })

    def record_error_rate(self, errors: int, total: int):
        """Record error rate"""
        rate = (errors / total * 100) if total > 0 else 0
        self.metrics.record("error_rate", rate)

        # Alert if error rate is high
        if rate > 10:
            self.alerts.append({
                "timestamp": datetime.now().isoformat(),
                "severity": "critical",
                "message": f"Error rate is {rate}% (> 10%)",
                "type": "reliability"
            })

    def record_token_usage(self, tokens: int):
        """Record token usage"""
        self.metrics.record("token_usage", tokens)

    def get_uptime(self) -> float:
        """Get system uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()

    def get_health_status(self) -> Dict:
        """Get overall health status"""
        error_rate_stats = self.metrics.get_stats("error_rate")
        error_rate = error_rate_stats.get("latest", 0) if error_rate_stats else 0

        # Determine health
        if error_rate > 20 or len([a for a in self.alerts if a["severity"] == "critical"]) > 0:
            health = "critical"
        elif error_rate > 10 or len([a for a in self.alerts if a["severity"] == "warning"]) > 5:
            health = "degraded"
        else:
            health = "healthy"

        return {
            "status": health,
            "uptime_seconds": self.get_uptime(),
            "error_rate": error_rate,
            "recent_alerts": len([
                a for a in self.alerts
                if datetime.fromisoformat(a["timestamp"]) > datetime.now() - timedelta(hours=1)
            ]),
            "metrics": self.metrics.get_all_stats()
        }


class BehaviorTracker:
    """Track and analyze agent behavior patterns"""

    def __init__(self):
        self.behaviors: Dict[str, List[Dict]] = defaultdict(list)
        self.patterns: Dict[str, Dict] = {}

    def track_decision(self, agent_id: str, decision: Dict):
        """Track an agent decision"""
        self.behaviors[agent_id].append({
            "type": "decision",
            "data": decision,
            "timestamp": datetime.now().isoformat()
        })

        self._analyze_patterns(agent_id)

    def track_communication(self, from_agent: str, to_agent: str, message_type: str):
        """Track agent communication"""
        self.behaviors[from_agent].append({
            "type": "communication",
            "to": to_agent,
            "message_type": message_type,
            "timestamp": datetime.now().isoformat()
        })

    def track_tool_use(self, agent_id: str, tool: str, success: bool):
        """Track tool usage"""
        self.behaviors[agent_id].append({
            "type": "tool_use",
            "tool": tool,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def _analyze_patterns(self, agent_id: str):
        """Analyze behavior patterns for an agent"""
        behaviors = self.behaviors[agent_id]
        if len(behaviors) < 10:
            return

        recent = behaviors[-100:]  # Last 100 behaviors

        # Analyze decision patterns
        decisions = [b for b in recent if b["type"] == "decision"]
        communications = [b for b in recent if b["type"] == "communication"]
        tool_uses = [b for b in recent if b["type"] == "tool_use"]

        self.patterns[agent_id] = {
            "decision_frequency": len(decisions) / len(recent),
            "communication_frequency": len(communications) / len(recent),
            "tool_use_frequency": len(tool_uses) / len(recent),
            "success_rate": sum(1 for t in tool_uses if t.get("success", False)) / max(len(tool_uses), 1),
            "most_contacted": self._most_common([c["to"] for c in communications]),
            "favorite_tools": self._most_common([t["tool"] for t in tool_uses])
        }

    def _most_common(self, items: List[str]) -> str:
        """Find most common item"""
        if not items:
            return None
        counts = defaultdict(int)
        for item in items:
            counts[item] += 1
        return max(counts, key=counts.get)

    def get_agent_profile(self, agent_id: str) -> Dict:
        """Get behavioral profile for an agent"""
        return {
            "total_behaviors": len(self.behaviors[agent_id]),
            "patterns": self.patterns.get(agent_id, {}),
            "recent_activity": self.behaviors[agent_id][-10:]
        }


class Observer:
    """
    Central observation system
    Monitors all aspects of Orchestra Town
    """

    def __init__(self):
        self.events: deque = deque(maxlen=1000)  # Keep last 1000 events
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)

        self.performance_monitor = PerformanceMonitor()
        self.behavior_tracker = BehaviorTracker()
        self.metrics = MetricCollector()

        # Anomaly detection
        self.anomalies: List[Dict] = []

    def emit(self, event_type: EventType, data: Dict, source: str = None):
        """Emit an observable event"""
        event = Event(event_type, data, source)
        self.events.append(event)

        # Notify subscribers
        for callback in self.subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                print(f"Observer callback error: {e}")

        # Track in behavior tracker
        if source:
            if event_type == EventType.TASK_ASSIGNED:
                self.behavior_tracker.track_decision(source, data)
            elif event_type == EventType.MESSAGE_SENT:
                self.behavior_tracker.track_communication(
                    source,
                    data.get("to_agent"),
                    data.get("message_type")
                )
            elif event_type == EventType.UTILITY_CALLED:
                self.behavior_tracker.track_tool_use(
                    source,
                    data.get("utility"),
                    data.get("success", True)
                )

        # Performance tracking
        if event_type == EventType.TASK_COMPLETED:
            duration = data.get("duration_seconds", 0)
            self.performance_monitor.record_task_time(data.get("task_id"), duration)

        # Detect anomalies
        self._detect_anomalies(event)

    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to events"""
        self.subscribers[event_type].append(callback)

    def _detect_anomalies(self, event: Event):
        """Detect anomalous behavior"""
        # Unusual error rate
        if event.type == EventType.TASK_FAILED:
            recent_failures = sum(
                1 for e in list(self.events)[-20:]
                if e.type == EventType.TASK_FAILED
            )

            if recent_failures > 5:  # More than 5 failures in last 20 events
                self.anomalies.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "high_failure_rate",
                    "description": f"{recent_failures} failures in recent 20 events",
                    "severity": "high"
                })

        # Unusual bias detection
        if event.type == EventType.BIAS_DETECTED:
            bias_score = event.data.get("bias_score", 0)
            if bias_score > 75:
                self.anomalies.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "high_bias_detected",
                    "description": f"Bias score: {bias_score}%",
                    "severity": "medium",
                    "source": event.source
                })

    def get_event_stream(self, event_type: EventType = None, limit: int = 100) -> List[Dict]:
        """Get event stream"""
        events = list(self.events)

        if event_type:
            events = [e for e in events if e.type == event_type]

        return [e.to_dict() for e in events[-limit:]]

    def get_realtime_dashboard(self) -> Dict:
        """Get real-time dashboard data"""
        recent_events = list(self.events)[-50:]

        return {
            "health": self.performance_monitor.get_health_status(),
            "recent_events": [e.to_dict() for e in recent_events],
            "event_counts": {
                et.value: sum(1 for e in recent_events if e.type == et)
                for et in EventType
            },
            "anomalies": self.anomalies[-10:],
            "alerts": self.performance_monitor.alerts[-10:],
            "system_metrics": self.metrics.get_all_stats()
        }

    def get_agent_insights(self, agent_id: str) -> Dict:
        """Get detailed insights for an agent"""
        return {
            "behavioral_profile": self.behavior_tracker.get_agent_profile(agent_id),
            "recent_events": [
                e.to_dict() for e in list(self.events)
                if e.source == agent_id
            ][-20:],
            "performance": {
                "utilization": self.performance_monitor.metrics.get_stats(
                    f"agent_{agent_id}_utilization"
                )
            }
        }

    def generate_report(self, time_window_hours: int = 24) -> Dict:
        """Generate comprehensive observation report"""
        cutoff = datetime.now() - timedelta(hours=time_window_hours)
        events_in_window = [
            e for e in self.events
            if e.timestamp > cutoff
        ]

        return {
            "report_period": f"Last {time_window_hours} hours",
            "total_events": len(events_in_window),
            "events_by_type": {
                et.value: sum(1 for e in events_in_window if e.type == et)
                for et in EventType
            },
            "health_summary": self.performance_monitor.get_health_status(),
            "anomalies_detected": len([
                a for a in self.anomalies
                if datetime.fromisoformat(a["timestamp"]) > cutoff
            ]),
            "top_agents_by_activity": self._get_top_agents(events_in_window),
            "performance_metrics": self.performance_monitor.metrics.get_all_stats()
        }

    def _get_top_agents(self, events: List[Event], limit: int = 5) -> List[Dict]:
        """Get most active agents"""
        agent_activity = defaultdict(int)
        for event in events:
            if event.source:
                agent_activity[event.source] += 1

        top = sorted(agent_activity.items(), key=lambda x: x[1], reverse=True)[:limit]

        return [
            {"agent_id": agent_id, "event_count": count}
            for agent_id, count in top
        ]


# Global observer instance
global_observer = Observer()


# Decorator for observable functions
def observable(event_type: EventType):
    """Decorator to make functions observable"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Emit event
            global_observer.emit(
                event_type,
                {"function": func.__name__, "result": str(result)[:100]},
                source=func.__name__
            )

            return result
        return wrapper
    return decorator
