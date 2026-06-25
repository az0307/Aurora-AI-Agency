"""
VirusTotal Enrichment Module for Kali Agent
Provides file hash, URL, IP, and domain reputation lookups.
Integrates with threat-intel skill for finding enrichment.

Requires: VIRUSTOTAL_API_KEY environment variable
Free tier: 4 requests/minute, 500/day

AutoBoros.ai | 2026-03-27
"""

import os
import json
import time
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote

VT_API_BASE = "https://www.virustotal.com/api/v3"
VT_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY", "")

# Rate limiting for free tier
_last_request_time = 0
RATE_LIMIT_SECONDS = 16  # 4 req/min = 1 every 15s, add 1s buffer


def _rate_limit():
    """Enforce rate limiting for free tier."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - elapsed)
    _last_request_time = time.time()


def _vt_request(endpoint: str) -> Optional[dict]:
    """Make a VirusTotal API request."""
    if not VT_API_KEY:
        return {"error": "VIRUSTOTAL_API_KEY not set"}

    _rate_limit()

    url = f"{VT_API_BASE}/{endpoint}"
    req = Request(url, headers={"x-apikey": VT_API_KEY})

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except URLError as e:
        return {"error": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def lookup_file_hash(file_hash: str) -> dict:
    """
    Look up a file hash (MD5, SHA1, SHA256) on VirusTotal.
    Returns detection stats, threat label, and sandbox results.
    """
    result = _vt_request(f"files/{file_hash}")
    if "error" in result:
        return result

    attrs = result.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})

    return {
        "hash": file_hash,
        "type": "file",
        "detection_stats": {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "undetected": stats.get("undetected", 0),
            "total": sum(stats.values()),
        },
        "threat_label": attrs.get("popular_threat_classification", {}).get("suggested_threat_label"),
        "file_type": attrs.get("type_description"),
        "file_size": attrs.get("size"),
        "first_seen": attrs.get("first_submission_date"),
        "last_seen": attrs.get("last_analysis_date"),
        "names": attrs.get("names", [])[:5],
        "tags": attrs.get("tags", [])[:10],
    }


def lookup_url(url: str) -> dict:
    """Look up a URL on VirusTotal for reputation and detections."""
    import base64
    url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
    result = _vt_request(f"urls/{url_id}")
    if "error" in result:
        return result

    attrs = result.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})

    return {
        "url": url,
        "type": "url",
        "detection_stats": {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
        },
        "final_url": attrs.get("last_final_url"),
        "title": attrs.get("title"),
        "last_analysis_date": attrs.get("last_analysis_date"),
        "categories": attrs.get("categories", {}),
    }


def lookup_ip(ip: str) -> dict:
    """Look up an IP address on VirusTotal for reputation."""
    result = _vt_request(f"ip_addresses/{ip}")
    if "error" in result:
        return result

    attrs = result.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})

    return {
        "ip": ip,
        "type": "ip",
        "detection_stats": {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
        },
        "country": attrs.get("country"),
        "as_owner": attrs.get("as_owner"),
        "asn": attrs.get("asn"),
        "reputation": attrs.get("reputation", 0),
        "last_analysis_date": attrs.get("last_analysis_date"),
    }


def lookup_domain(domain: str) -> dict:
    """Look up a domain on VirusTotal for reputation."""
    result = _vt_request(f"domains/{domain}")
    if "error" in result:
        return result

    attrs = result.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})

    return {
        "domain": domain,
        "type": "domain",
        "detection_stats": {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
        },
        "registrar": attrs.get("registrar"),
        "creation_date": attrs.get("creation_date"),
        "reputation": attrs.get("reputation", 0),
        "categories": attrs.get("categories", {}),
        "last_dns_records": attrs.get("last_dns_records", [])[:5],
    }


def enrich_finding(finding: dict) -> dict:
    """
    Auto-enrich a pentest finding with VT intelligence.
    Checks IPs, domains, and any hashes found in the finding.
    """
    enrichments = []

    # Check affected asset
    asset = finding.get("affected_asset", "")
    if asset:
        # Try as IP first
        import re
        ip_match = re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', asset)
        if ip_match:
            enrichments.append(lookup_ip(asset))
        else:
            # Extract domain
            domain = asset.split("://")[-1].split("/")[0].split(":")[0]
            if "." in domain:
                enrichments.append(lookup_domain(domain))

    finding["vt_enrichment"] = enrichments
    return finding
