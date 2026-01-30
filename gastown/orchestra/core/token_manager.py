"""
Token and Context Management System
Tracks token usage, manages context windows, prevents bloat and bias
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import tiktoken


class TokenCounter:
    """Count tokens using tiktoken (OpenAI's tokenizer)"""

    def __init__(self, model: str = "cl100k_base"):
        try:
            self.encoding = tiktoken.get_encoding(model)
        except:
            # Fallback to approximate counting
            self.encoding = None

    def count(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4

    def count_messages(self, messages: List[Dict]) -> int:
        """Count tokens in message list"""
        total = 0
        for msg in messages:
            total += self.count(str(msg.get('content', '')))
        return total


class ContextWindow:
    """Manages context window for a conversation/agent"""

    def __init__(self, max_tokens: int = 200000, model: str = "sonnet-4"):
        self.max_tokens = max_tokens
        self.model = model
        self.messages: List[Dict] = []
        self.token_count = 0
        self.counter = TokenCounter()
        self.summary: Optional[str] = None
        self.compression_history: List[Dict] = []

    def add_message(self, role: str, content: str, metadata: Dict = None) -> bool:
        """Add message to context window"""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "tokens": self.counter.count(content)
        }

        # Check if we need to compress
        if self.token_count + msg["tokens"] > self.max_tokens * 0.9:  # 90% threshold
            self._compress_context()

        self.messages.append(msg)
        self.token_count += msg["tokens"]
        return True

    def _compress_context(self):
        """Compress context using summarization"""
        if len(self.messages) < 10:
            return  # Not enough to compress

        # Take first half of messages for summarization
        to_summarize = self.messages[:len(self.messages)//2]

        # Create summary
        summary_text = self._create_summary(to_summarize)
        summary_tokens = self.counter.count(summary_text)

        # Record compression
        self.compression_history.append({
            "timestamp": datetime.now().isoformat(),
            "original_messages": len(to_summarize),
            "original_tokens": sum(m["tokens"] for m in to_summarize),
            "summary_tokens": summary_tokens,
            "compression_ratio": summary_tokens / sum(m["tokens"] for m in to_summarize)
        })

        # Replace summarized messages with summary
        self.messages = [
            {
                "role": "system",
                "content": f"[CONTEXT SUMMARY] {summary_text}",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"type": "compression_summary"},
                "tokens": summary_tokens
            }
        ] + self.messages[len(to_summarize):]

        # Update token count
        self.token_count = sum(m["tokens"] for m in self.messages)
        self.summary = summary_text

    def _create_summary(self, messages: List[Dict]) -> str:
        """Create summary of messages"""
        # Extract key information
        user_queries = []
        assistant_responses = []
        actions = []

        for msg in messages:
            if msg["role"] == "user":
                user_queries.append(msg["content"][:100])  # First 100 chars
            elif msg["role"] == "assistant":
                assistant_responses.append(msg["content"][:100])
            elif msg.get("metadata", {}).get("type") == "action":
                actions.append(msg["content"][:50])

        summary = f"""Previous conversation summary:
- User queries: {len(user_queries)} questions/requests
- Key topics: {', '.join(user_queries[:3])}
- Actions taken: {len(actions)} operations
- Main responses: {len(assistant_responses)} messages
"""
        return summary

    def get_stats(self) -> Dict:
        """Get context window statistics"""
        return {
            "total_messages": len(self.messages),
            "total_tokens": self.token_count,
            "max_tokens": self.max_tokens,
            "utilization": (self.token_count / self.max_tokens) * 100,
            "compressions": len(self.compression_history),
            "has_summary": self.summary is not None
        }


class TokenBudget:
    """Manages token budgets for different operations"""

    def __init__(self, total_budget: int = 1000000):
        self.total_budget = total_budget
        self.remaining = total_budget
        self.allocations: Dict[str, int] = {}
        self.usage: Dict[str, int] = defaultdict(int)
        self.operations: List[Dict] = []

    def allocate(self, category: str, tokens: int) -> bool:
        """Allocate tokens to a category"""
        if tokens > self.remaining:
            return False

        self.allocations[category] = tokens
        self.remaining -= tokens
        return True

    def use_tokens(self, category: str, tokens: int, operation: str = None) -> bool:
        """Use tokens from a category"""
        if category not in self.allocations:
            return False

        if self.usage[category] + tokens > self.allocations[category]:
            return False

        self.usage[category] += tokens
        self.operations.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "tokens": tokens,
            "operation": operation,
            "total_used": self.usage[category],
            "allocation": self.allocations[category]
        })

        return True

    def get_usage_report(self) -> Dict:
        """Get detailed usage report"""
        report = {
            "total_budget": self.total_budget,
            "total_used": sum(self.usage.values()),
            "remaining": self.remaining,
            "categories": {}
        }

        for category, allocated in self.allocations.items():
            used = self.usage[category]
            report["categories"][category] = {
                "allocated": allocated,
                "used": used,
                "remaining": allocated - used,
                "utilization": (used / allocated * 100) if allocated > 0 else 0
            }

        return report


class BiasDetector:
    """Detect and mitigate bias in agent responses"""

    def __init__(self):
        self.bias_patterns = {
            "confirmation_bias": [
                "always", "never", "everyone knows", "obviously",
                "it's clear that", "without a doubt"
            ],
            "recency_bias": [
                "just", "recently", "latest", "newest",
                "most recent"
            ],
            "anchoring_bias": [
                "first", "initial", "originally"
            ],
            "availability_bias": [
                "common", "typical", "usual", "normally"
            ]
        }

        self.detections: List[Dict] = []

    def analyze(self, text: str) -> Dict:
        """Analyze text for bias indicators"""
        text_lower = text.lower()
        detected_biases = defaultdict(list)

        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    detected_biases[bias_type].append(pattern)

        # Calculate bias score
        total_indicators = sum(len(v) for v in detected_biases.values())
        bias_score = min(total_indicators / 10 * 100, 100)  # Max 100%

        result = {
            "bias_score": bias_score,
            "detected_biases": dict(detected_biases),
            "severity": self._get_severity(bias_score),
            "recommendations": self._get_recommendations(detected_biases)
        }

        self.detections.append({
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "text_length": len(text)
        })

        return result

    def _get_severity(self, score: float) -> str:
        """Get severity level"""
        if score < 20:
            return "low"
        elif score < 50:
            return "medium"
        elif score < 75:
            return "high"
        else:
            return "critical"

    def _get_recommendations(self, biases: Dict) -> List[str]:
        """Get recommendations to reduce bias"""
        recommendations = []

        if "confirmation_bias" in biases:
            recommendations.append("Use more tentative language like 'may', 'could', 'often'")
            recommendations.append("Present alternative perspectives")

        if "recency_bias" in biases:
            recommendations.append("Include historical context")
            recommendations.append("Balance recent and established information")

        if "anchoring_bias" in biases:
            recommendations.append("Consider multiple starting points")
            recommendations.append("Re-evaluate initial assumptions")

        if "availability_bias" in biases:
            recommendations.append("Seek less obvious examples")
            recommendations.append("Include statistical data")

        return recommendations


class QualityMetrics:
    """Track quality metrics for agent outputs"""

    def __init__(self):
        self.metrics: List[Dict] = []

    def evaluate(self, output: str, context: Dict = None) -> Dict:
        """Evaluate output quality"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "length": len(output),
            "word_count": len(output.split()),
            "has_code": "```" in output,
            "has_list": any(line.strip().startswith(('-', '*', '1.')) for line in output.split('\n')),
            "has_links": "http" in output or "https" in output,
            "structure_score": self._evaluate_structure(output),
            "clarity_score": self._evaluate_clarity(output),
            "completeness_score": self._evaluate_completeness(output, context)
        }

        # Overall quality score
        metrics["quality_score"] = (
            metrics["structure_score"] * 0.3 +
            metrics["clarity_score"] * 0.4 +
            metrics["completeness_score"] * 0.3
        )

        self.metrics.append(metrics)
        return metrics

    def _evaluate_structure(self, text: str) -> float:
        """Evaluate structural quality (0-100)"""
        score = 0

        # Has headers
        if any(line.startswith('#') for line in text.split('\n')):
            score += 25

        # Has paragraphs
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            score += 25

        # Has lists or code blocks
        if any(marker in text for marker in ['```', '- ', '* ', '1. ']):
            score += 25

        # Reasonable length
        if 100 < len(text) < 5000:
            score += 25

        return min(score, 100)

    def _evaluate_clarity(self, text: str) -> float:
        """Evaluate clarity (0-100)"""
        score = 100

        # Check for overly long sentences
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if avg_sentence_length > 30:
            score -= 20

        # Check for jargon overload
        complex_words = len([w for w in text.split() if len(w) > 12])
        if complex_words / max(len(text.split()), 1) > 0.1:
            score -= 15

        # Positive: Has examples
        if "example" in text.lower() or "for instance" in text.lower():
            score += 10

        return max(min(score, 100), 0)

    def _evaluate_completeness(self, text: str, context: Dict = None) -> float:
        """Evaluate completeness (0-100)"""
        score = 50  # Base score

        # Has introduction/conclusion
        if len(text) > 200:
            score += 15

        # Addresses context if provided
        if context and context.get("requirements"):
            for req in context["requirements"]:
                if req.lower() in text.lower():
                    score += 10

        # Has actionable content
        action_words = ["step", "how to", "instructions", "guide"]
        if any(word in text.lower() for word in action_words):
            score += 15

        return min(score, 100)

    def get_trend_analysis(self) -> Dict:
        """Get trend analysis of quality over time"""
        if not self.metrics:
            return {}

        recent = self.metrics[-10:]  # Last 10 outputs

        return {
            "average_quality": sum(m["quality_score"] for m in recent) / len(recent),
            "average_length": sum(m["length"] for m in recent) / len(recent),
            "structure_trend": sum(m["structure_score"] for m in recent) / len(recent),
            "clarity_trend": sum(m["clarity_score"] for m in recent) / len(recent),
            "total_evaluations": len(self.metrics)
        }


class TokenManager:
    """
    Central token and context management system
    Prevents bloat, detects bias, ensures quality
    """

    def __init__(self, total_budget: int = 1000000):
        self.budget = TokenBudget(total_budget)
        self.contexts: Dict[str, ContextWindow] = {}
        self.bias_detector = BiasDetector()
        self.quality_metrics = QualityMetrics()
        self.counter = TokenCounter()

    def create_context(self, agent_id: str, max_tokens: int = 200000):
        """Create a new context window for an agent"""
        self.contexts[agent_id] = ContextWindow(max_tokens)

    def add_to_context(self, agent_id: str, role: str, content: str, metadata: Dict = None):
        """Add message to agent's context"""
        if agent_id not in self.contexts:
            self.create_context(agent_id)

        self.contexts[agent_id].add_message(role, content, metadata)

    def evaluate_output(self, output: str, check_bias: bool = True, check_quality: bool = True) -> Dict:
        """Comprehensive output evaluation"""
        result = {
            "tokens": self.counter.count(output),
            "timestamp": datetime.now().isoformat()
        }

        if check_bias:
            result["bias_analysis"] = self.bias_detector.analyze(output)

        if check_quality:
            result["quality_metrics"] = self.quality_metrics.evaluate(output)

        return result

    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics"""
        return {
            "token_budget": self.budget.get_usage_report(),
            "active_contexts": len(self.contexts),
            "context_stats": {
                agent_id: ctx.get_stats()
                for agent_id, ctx in self.contexts.items()
            },
            "bias_detections": len(self.bias_detector.detections),
            "quality_trends": self.quality_metrics.get_trend_analysis()
        }
