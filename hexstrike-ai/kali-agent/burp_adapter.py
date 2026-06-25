"""
Burp Suite REST API Adapter for Kali Agent
Wraps Burp Suite Professional's REST API for automated scanning.

Requires: Burp Suite Professional running with REST API enabled
  Burp → User Options → Misc → REST API → Enable, set port (default 1337)

AutoBoros.ai | 2026-03-27
"""

import json
import time
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BURP_API_BASE = "http://127.0.0.1:1337/v0.1"
BURP_API_KEY = ""  # Set if API key authentication is enabled


def _burp_request(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Make a Burp Suite REST API request."""
    url = f"{BURP_API_BASE}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    if BURP_API_KEY:
        headers["Authorization"] = f"Bearer {BURP_API_KEY}"

    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req, timeout=30) as response:
            if response.status == 204:
                return {"status": "ok"}
            return json.loads(response.read().decode())
    except HTTPError as e:
        return {"error": f"Burp API returned HTTP {e.code}: {e.reason}"}
    except URLError as e:
        return {"error": f"Cannot reach Burp API at {BURP_API_BASE}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# SCANNING
# ============================================================

def start_active_scan(target_url: str, config: Optional[dict] = None) -> dict:
    """
    Start a Burp active scan against a target URL.
    Returns scan task ID for polling.
    """
    payload = {"urls": [target_url]}
    if config:
        payload["scan_configurations"] = config

    result = _burp_request("POST", "scan", payload)
    if "error" in result:
        return result

    return {
        "status": "scan_started",
        "target": target_url,
        "task_location": result.get("task_id", "unknown"),
    }


def get_scan_status(task_id: str) -> dict:
    """Get the status of a running scan."""
    return _burp_request("GET", f"scan/{task_id}")


def wait_for_scan(task_id: str, timeout: int = 3600, poll_interval: int = 10) -> dict:
    """
    Poll scan status until completion or timeout.
    Returns final scan results.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = get_scan_status(task_id)
        if "error" in status:
            return status

        scan_status = status.get("scan_status", "unknown")
        if scan_status in ("succeeded", "failed", "cancelled"):
            return status

        metrics = status.get("scan_metrics", {})
        print(f"  Scan progress: {metrics.get('crawl_requests_made', 0)} crawled, "
              f"{metrics.get('audit_requests_made', 0)} audited, "
              f"issues: {metrics.get('total_issues', 0)}")

        time.sleep(poll_interval)

    return {"error": f"Scan timed out after {timeout}s", "task_id": task_id}


# ============================================================
# ISSUES (FINDINGS)
# ============================================================

def get_scan_issues(task_id: Optional[str] = None) -> dict:
    """
    Get issues (findings) from Burp.
    If task_id provided, gets issues for that scan only.
    Otherwise gets all issues from the current project.
    """
    if task_id:
        return _burp_request("GET", f"scan/{task_id}")
    return _burp_request("GET", "knowledge_base/issue_definitions")


def convert_issues_to_findings(burp_issues: list) -> list:
    """
    Convert Burp Suite issues to Kali Agent finding format
    for integration with vuln-analysis and red-team-report skills.
    """
    severity_map = {
        "high": "high",
        "medium": "medium",
        "low": "low",
        "information": "info",
    }

    findings = []
    for i, issue in enumerate(burp_issues):
        findings.append({
            "id": f"BURP-{str(i + 1).padStart(3, '0') if hasattr(str, 'padStart') else f'{i+1:03d}'}",
            "severity": severity_map.get(issue.get("severity", "").lower(), "info"),
            "title": issue.get("issue_name", issue.get("name", "Unknown Issue")),
            "affected_asset": issue.get("origin", "") + issue.get("path", ""),
            "tool": "burpsuite",
            "description": issue.get("issue_detail", issue.get("description", "")),
            "remediation": issue.get("remediation_detail", issue.get("remediation", "")),
            "confidence": issue.get("confidence", "certain"),
            "cwe": issue.get("type_index"),
            "evidence": issue.get("evidence", ""),
        })
    return findings


# ============================================================
# SITEMAP & PROXY
# ============================================================

def get_sitemap() -> dict:
    """Get the current Burp Suite sitemap."""
    return _burp_request("GET", "sitemap")


def get_proxy_history(limit: int = 100) -> dict:
    """Get recent proxy history entries."""
    return _burp_request("GET", f"proxy/history?limit={limit}")


# ============================================================
# CONFIGURATION
# ============================================================

def get_scan_configurations() -> dict:
    """List available scan configurations."""
    return _burp_request("GET", "scan/configurations")


def check_burp_connection() -> dict:
    """
    Check if Burp Suite REST API is reachable.
    Returns connection status and version info.
    """
    result = _burp_request("GET", "")
    if "error" in result:
        return {
            "connected": False,
            "error": result["error"],
            "troubleshooting": [
                "Ensure Burp Suite Professional is running",
                "Enable REST API: User Options → Misc → REST API",
                f"Check API is listening on {BURP_API_BASE}",
                "Verify API key if authentication is enabled",
            ],
        }
    return {"connected": True, "info": result}


# ============================================================
# INTEGRATION WITH KALI AGENT PLAYBOOK
# ============================================================

def run_burp_scan_phase(target_url: str, scope_guard=None) -> dict:
    """
    Full Burp scan phase — validates scope, starts scan, waits, returns findings.
    Designed to be called from executePlaybook.js via HexStrike.
    """
    # Scope check
    if scope_guard:
        check = scope_guard.validate(target_url)
        if not check["allowed"]:
            return {"status": "blocked", "reason": check["reason"]}

    # Check connection
    conn = check_burp_connection()
    if not conn["connected"]:
        return {"status": "error", "message": "Burp Suite not reachable", "details": conn}

    # Start scan
    scan_result = start_active_scan(target_url)
    if "error" in scan_result:
        return {"status": "error", "message": scan_result["error"]}

    task_id = scan_result.get("task_location")
    if not task_id:
        return {"status": "error", "message": "No task ID returned from Burp"}

    # Wait for completion
    final = wait_for_scan(task_id, timeout=1800)
    if "error" in final:
        return {"status": "error", "message": final["error"]}

    # Extract and convert issues
    issues = final.get("issue_events", [])
    findings = convert_issues_to_findings(issues)

    return {
        "status": "success",
        "target": target_url,
        "scan_duration": final.get("scan_metrics", {}).get("total_elapsed_time"),
        "findings_count": len(findings),
        "findings": findings,
    }
