import os
import json

from scanner.header_scanner import scan_headers
from scanner.ssl_scanner import get_ssl_info
from scanner.score_engine import calculate_score
from scanner.tech_detector import detect_technology
from scanner.nmap_scanner import scan_ports
from scanner.nikto_scanner import scan_with_nikto
from scanner.nessus_scanner import scan_with_nessus
from scanner.utils import safe_target_or_raise, UnsafeTargetError

# Feature toggles so a deployment without nikto/nessus installed/licensed
# still runs the free, always-available checks (headers, SSL, tech, nmap).
ENABLE_NMAP = os.getenv("ENABLE_NMAP", "true").lower() == "true"
ENABLE_NIKTO = os.getenv("ENABLE_NIKTO", "true").lower() == "true"
ENABLE_NESSUS = os.getenv("ENABLE_NESSUS", "false").lower() == "true"


def scan_website(url: str) -> dict:
    """
    Run the full SecureLens audit against `url` and return a single
    combined report. Raises UnsafeTargetError if the target resolves to a
    private/internal address (see scanner/utils.py) — callers should catch
    this and return a 400 to the client rather than letting the scan run.
    """
    normalized_url, hostname = safe_target_or_raise(url)

    header_results = scan_headers(normalized_url)
    ssl_results = get_ssl_info(normalized_url)
    technology_results = detect_technology(normalized_url)

    nmap_results = (
        scan_ports(normalized_url)
        if ENABLE_NMAP
        else {"enabled": False, "open_ports": []}
    )

    nikto_results = (
        scan_with_nikto(normalized_url)
        if ENABLE_NIKTO
        else {"enabled": False, "findings": []}
    )

    nessus_results = (
        scan_with_nessus(hostname)
        if ENABLE_NESSUS
        else {"enabled": False, "findings": []}
    )

    score_results = calculate_score(
        header_results,
        ssl_results,
        nmap_results,
        nikto_results,
        nessus_results,
    )

    report = {
        "target": normalized_url,
        "score": score_results,
        "headers": header_results,
        "ssl": ssl_results,
        "technology": technology_results,
        "nmap": nmap_results,
        "nikto": nikto_results,
        "nessus": nessus_results,
    }

    return report


if __name__ == "__main__":
    url = input("Enter URL: ").strip()

    try:
        report = scan_website(url)
    except UnsafeTargetError as e:
        print(f"Refused: {e}")
    else:
        print("\n=== SECURELENS REPORT ===\n")
        print(json.dumps(report, indent=4))
