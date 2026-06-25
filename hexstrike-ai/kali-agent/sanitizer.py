"""
ToolOutputSanitizer — Prompt injection protection for AI-driven pentesting
Drop into HexStrike's response pipeline.
AutoBoros.ai | 2026-03-27
"""

import re
from typing import Optional


# Patterns that indicate prompt injection attempts in tool output
INJECTION_TAG_PATTERNS = [
    re.compile(r'<\s*system\s*>.*?<\s*/\s*system\s*>', re.I | re.DOTALL),
    re.compile(r'<\s*assistant\s*>.*?<\s*/\s*assistant\s*>', re.I | re.DOTALL),
    re.compile(r'<\s*human\s*>.*?<\s*/\s*human\s*>', re.I | re.DOTALL),
    re.compile(r'<\s*instructions?\s*>.*?<\s*/\s*instructions?\s*>', re.I | re.DOTALL),
    re.compile(r'<\s*prompt\s*>.*?<\s*/\s*prompt\s*>', re.I | re.DOTALL),
    re.compile(r'<\s*tool_use\s*>.*?<\s*/\s*tool_use\s*>', re.I | re.DOTALL),
    re.compile(r'<\s*anthr?opic\s*>.*?<\s*/\s*anthr?opic\s*>', re.I | re.DOTALL),
]

INJECTION_PHRASE_PATTERNS = [
    re.compile(r'ignore\s+(all\s+)?previous\s+instructions?', re.I),
    re.compile(r'you\s+are\s+now\s+in\s+.{0,30}(unrestricted|admin|god|jailbreak)\s+mode', re.I),
    re.compile(r'forget\s+(all\s+)?(your\s+)?rules', re.I),
    re.compile(r'new\s+instruction[s]?\s*:', re.I),
    re.compile(r'override\s+(all\s+)?safety', re.I),
    re.compile(r'disregard\s+(all\s+)?prior', re.I),
    re.compile(r'from\s+now\s+on\s+you\s+(are|will|must)', re.I),
    re.compile(r'system\s*:\s*you\s+(are|will|must)', re.I),
    re.compile(r'IMPORTANT\s*:?\s*(ignore|forget|disregard|override)', re.I),
    re.compile(r'(act|behave|respond)\s+as\s+(if|though)\s+you\s+(are|were)', re.I),
    re.compile(r'do\s+not\s+follow\s+(your\s+)?(safety|content|ethical)', re.I),
]

# Per-tool output limits (characters)
TOOL_OUTPUT_LIMITS = {
    "nmap": 100_000,
    "nuclei": 100_000,
    "sqlmap": 50_000,
    "nikto": 50_000,
    "ffuf": 80_000,
    "gobuster": 80_000,
    "hydra": 30_000,
    "hashcat": 20_000,
    "john": 20_000,
    "whatweb": 20_000,
    "subfinder": 50_000,
    "amass": 100_000,
    "theHarvester": 30_000,
    "searchsploit": 30_000,
    "crackmapexec": 50_000,
    "responder": 30_000,
    "tshark": 80_000,
    "tcpdump": 50_000,
    "curl": 30_000,
    "default": 50_000,
}


class SanitizationResult:
    """Result of sanitization with metadata about what was cleaned."""

    def __init__(self, output: str, tags_removed: int = 0, phrases_neutralized: int = 0, truncated: bool = False):
        self.output = output
        self.tags_removed = tags_removed
        self.phrases_neutralized = phrases_neutralized
        self.truncated = truncated
        self.was_modified = tags_removed > 0 or phrases_neutralized > 0 or truncated

    def to_dict(self) -> dict:
        return {
            "sanitized_output": self.output,
            "tags_removed": self.tags_removed,
            "phrases_neutralized": self.phrases_neutralized,
            "truncated": self.truncated,
            "was_modified": self.was_modified,
        }


def sanitize_tool_output(
    raw_output: str,
    tool_name: str = "unknown",
    max_length: Optional[int] = None,
    add_data_fence: bool = True,
) -> SanitizationResult:
    """
    Sanitize tool output to prevent prompt injection before feeding to Claude.

    Args:
        raw_output: Raw string output from a security tool
        tool_name: Name of the tool that produced the output
        max_length: Override max length (defaults to per-tool limit)
        add_data_fence: Wrap output in [BEGIN/END TOOL OUTPUT] markers

    Returns:
        SanitizationResult with cleaned output and modification metadata
    """
    output = raw_output
    tags_removed = 0
    phrases_neutralized = 0
    truncated = False

    # 1. Truncate oversized output
    limit = max_length or TOOL_OUTPUT_LIMITS.get(tool_name, TOOL_OUTPUT_LIMITS["default"])
    if len(output) > limit:
        output = output[:limit] + f"\n[TRUNCATED — original size: {len(raw_output)} chars]"
        truncated = True

    # 2. Strip XML/HTML tags that mimic system prompts
    for pattern in INJECTION_TAG_PATTERNS:
        matches = pattern.findall(output)
        if matches:
            tags_removed += len(matches)
            output = pattern.sub("[SANITIZED: suspicious markup removed]", output)

    # 3. Neutralize prompt injection phrases
    for pattern in INJECTION_PHRASE_PATTERNS:
        matches = pattern.findall(output)
        if matches:
            phrases_neutralized += len(matches)
            output = pattern.sub("[SANITIZED: injection pattern detected]", output)

    # 4. Strip triple-backtick blocks that could be interpreted as code execution
    # (common in HTTP responses that try to inject markdown)
    output = re.sub(
        r'```\s*(system|assistant|human|instructions?).*?```',
        '[SANITIZED: suspicious code block removed]',
        output,
        flags=re.I | re.DOTALL,
    )

    # 5. Wrap in data fence markers
    if add_data_fence:
        output = f"[BEGIN TOOL OUTPUT: {tool_name}]\n{output}\n[END TOOL OUTPUT: {tool_name}]"

    return SanitizationResult(
        output=output,
        tags_removed=tags_removed,
        phrases_neutralized=phrases_neutralized,
        truncated=truncated,
    )


def sanitize_nmap_output(raw_output: str) -> SanitizationResult:
    """Nmap-specific sanitization — strips oversized NSE script output."""
    # Limit NSE script output to 500 chars per script block
    output = re.sub(
        r'(\|_?\s+\S+:)(.*?)(?=\n\||\nNmap|\Z)',
        lambda m: m.group(1) + m.group(2)[:500] + ("[TRUNCATED]" if len(m.group(2)) > 500 else ""),
        raw_output,
        flags=re.DOTALL,
    )
    return sanitize_tool_output(output, "nmap")


def sanitize_web_content(raw_html: str, max_size: int = 10_000) -> SanitizationResult:
    """Sanitize web page content fetched during testing."""
    output = raw_html
    # Strip all script tags entirely
    output = re.sub(r'<script[^>]*>.*?</script>', '', output, flags=re.I | re.DOTALL)
    # Strip style tags
    output = re.sub(r'<style[^>]*>.*?</style>', '', output, flags=re.I | re.DOTALL)
    # Strip HTML comments (common injection vector)
    output = re.sub(r'<!--.*?-->', '', output, flags=re.DOTALL)
    # Limit size
    if len(output) > max_size:
        output = output[:max_size] + "\n[TRUNCATED]"
    return sanitize_tool_output(output, "web_fetch")


def is_output_suspicious(raw_output: str) -> bool:
    """Quick check — does this output contain potential injection attempts?"""
    for pattern in INJECTION_TAG_PATTERNS + INJECTION_PHRASE_PATTERNS:
        if pattern.search(raw_output):
            return True
    return False
