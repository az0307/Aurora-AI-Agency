"""
Findings Deduplicator for Kali Agent
Merges overlapping vulnerability findings from multiple scanning tools.

Problem: nuclei, nikto, sqlmap, and Burp often report the same vulnerability
differently. This module normalises, deduplicates, and merges them.

AutoBoros.ai | 2026-03-27
"""

import re
from typing import Optional
from difflib import SequenceMatcher


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _normalise_url(url: str) -> str:
    """Normalise a URL for comparison."""
    url = url.lower().strip().rstrip("/")
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r':\d+', '', url)  # Strip port
    url = re.sub(r'[?#].*$', '', url)  # Strip query/fragment
    return url


def _normalise_cve(cve: Optional[str]) -> Optional[str]:
    """Normalise a CVE ID."""
    if not cve:
        return None
    match = re.search(r'CVE-\d{4}-\d+', cve.upper())
    return match.group(0) if match else None


def _title_similarity(a: str, b: str) -> float:
    """Score how similar two finding titles are (0.0 to 1.0)."""
    a_clean = re.sub(r'[^a-z0-9\s]', '', a.lower())
    b_clean = re.sub(r'[^a-z0-9\s]', '', b.lower())
    return SequenceMatcher(None, a_clean, b_clean).ratio()


def _asset_match(a: str, b: str) -> bool:
    """Check if two affected asset strings refer to the same target."""
    return _normalise_url(a) == _normalise_url(b)


def _merge_two_findings(primary: dict, secondary: dict) -> dict:
    """
    Merge two findings into one, keeping the best data from each.
    Primary finding takes precedence for most fields.
    """
    merged = {**primary}

    # Use highest severity
    if SEVERITY_ORDER.get(secondary.get("severity"), 5) < SEVERITY_ORDER.get(primary.get("severity"), 5):
        merged["severity"] = secondary["severity"]

    # Use highest CVSS
    if (secondary.get("cvss") or 0) > (primary.get("cvss") or 0):
        merged["cvss"] = secondary["cvss"]

    # Merge CVE (prefer non-null)
    if not merged.get("cve") and secondary.get("cve"):
        merged["cve"] = secondary["cve"]

    # Merge tools
    tools = set()
    for f in [primary, secondary]:
        tool = f.get("tool", "")
        if tool:
            tools.update(t.strip() for t in tool.split(","))
    merged["tool"] = ", ".join(sorted(tools))

    # Merge descriptions (keep longer one)
    if len(secondary.get("description", "")) > len(primary.get("description", "")):
        merged["description"] = secondary["description"]

    # Merge remediation (keep longer one)
    if len(secondary.get("remediation", "")) > len(primary.get("remediation", "")):
        merged["remediation"] = secondary["remediation"]

    # Merge evidence
    primary_evidence = primary.get("evidence", "")
    secondary_evidence = secondary.get("evidence", "")
    if secondary_evidence and secondary_evidence not in primary_evidence:
        merged["evidence"] = f"{primary_evidence}\n---\n{secondary_evidence}".strip()

    # Track merge source
    merged["merged_from"] = merged.get("merged_from", [primary.get("id", "?")])
    merged["merged_from"].append(secondary.get("id", "?"))

    # Track duplicate count
    merged["duplicate_count"] = merged.get("duplicate_count", 1) + 1

    return merged


def deduplicate_findings(findings: list, similarity_threshold: float = 0.6) -> list:
    """
    Deduplicate a list of vulnerability findings from multiple tools.

    Matching criteria (any one triggers a merge):
    1. Same CVE ID
    2. Same affected asset + similar title (above threshold)
    3. Same CWE + same affected asset

    Args:
        findings: List of finding dicts
        similarity_threshold: Title similarity threshold (0.0-1.0, default 0.6)

    Returns:
        Deduplicated list with merged findings
    """
    if not findings:
        return []

    merged = []
    used = set()

    # Sort by severity (critical first) so primary is always the most severe
    sorted_findings = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "info"), 5))

    for i, finding_a in enumerate(sorted_findings):
        if i in used:
            continue

        current = dict(finding_a)

        for j, finding_b in enumerate(sorted_findings):
            if j <= i or j in used:
                continue

            # Check CVE match
            cve_a = _normalise_cve(finding_a.get("cve"))
            cve_b = _normalise_cve(finding_b.get("cve"))
            if cve_a and cve_b and cve_a == cve_b:
                current = _merge_two_findings(current, finding_b)
                used.add(j)
                continue

            # Check asset + title similarity
            asset_a = finding_a.get("affected_asset", finding_a.get("asset", ""))
            asset_b = finding_b.get("affected_asset", finding_b.get("asset", ""))
            if asset_a and asset_b and _asset_match(asset_a, asset_b):
                title_a = finding_a.get("title", "")
                title_b = finding_b.get("title", "")
                if title_a and title_b and _title_similarity(title_a, title_b) >= similarity_threshold:
                    current = _merge_two_findings(current, finding_b)
                    used.add(j)
                    continue

            # Check CWE + asset match
            cwe_a = finding_a.get("cwe")
            cwe_b = finding_b.get("cwe")
            if cwe_a and cwe_b and cwe_a == cwe_b:
                if asset_a and asset_b and _asset_match(asset_a, asset_b):
                    current = _merge_two_findings(current, finding_b)
                    used.add(j)
                    continue

        merged.append(current)

    # Re-sort by severity
    merged.sort(key=lambda f: SEVERITY_ORDER.get(f.get("severity", "info"), 5))

    return merged


def dedup_stats(original: list, deduped: list) -> dict:
    """Return deduplication statistics."""
    removed = len(original) - len(deduped)
    merged_findings = [f for f in deduped if f.get("duplicate_count", 1) > 1]
    return {
        "original_count": len(original),
        "deduplicated_count": len(deduped),
        "removed": removed,
        "reduction_pct": round(removed / max(len(original), 1) * 100, 1),
        "merged_findings": len(merged_findings),
        "max_duplicates": max((f.get("duplicate_count", 1) for f in deduped), default=1),
    }
