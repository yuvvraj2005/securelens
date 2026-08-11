"""
Nessus integration.

Nessus (Tenable) isn't a CLI tool you shell out to — it's a daemon you talk
to over its REST API (default https://localhost:8834). This client assumes
you already have Nessus installed and licensed separately (it's commercial
software; SecureLens does not, and cannot, bundle or install it for you —
see scripts/setup.sh for a pointer to Tenable's installer).

Flow:
  1. Log in with an API access key + secret key (generate these in the
     Nessus web UI under Settings -> My Account -> API Keys), OR a
     username/password session token — API keys are recommended.
  2. Create a scan against the target using a policy template (defaults to
     "Basic Network Scan").
  3. Launch it, poll until it finishes.
  4. Pull the results and normalize them into the same
     {finding_count, findings: [...]} shape the other scanners use.

If Nessus isn't configured (no NESSUS_URL / keys in the environment) this
degrades gracefully and reports itself as disabled rather than erroring the
whole scan.
"""

import os
import time
import requests

NESSUS_URL = os.getenv("NESSUS_URL", "").rstrip("/")
NESSUS_ACCESS_KEY = os.getenv("NESSUS_ACCESS_KEY", "")
NESSUS_SECRET_KEY = os.getenv("NESSUS_SECRET_KEY", "")
# Nessus commonly runs behind a self-signed cert on localhost; make this
# opt-in rather than silently insecure by default in real deployments.
NESSUS_VERIFY_SSL = os.getenv("NESSUS_VERIFY_SSL", "false").lower() == "true"
NESSUS_POLL_INTERVAL_SECONDS = int(os.getenv("NESSUS_POLL_INTERVAL_SECONDS", "10"))
NESSUS_MAX_WAIT_SECONDS = int(os.getenv("NESSUS_MAX_WAIT_SECONDS", "1800"))
NESSUS_TEMPLATE_NAME = os.getenv("NESSUS_TEMPLATE_NAME", "basic")


def _configured() -> bool:
    return bool(NESSUS_URL and NESSUS_ACCESS_KEY and NESSUS_SECRET_KEY)


def _headers():
    return {
        "X-ApiKeys": f"accessKey={NESSUS_ACCESS_KEY}; secretKey={NESSUS_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def _get(path, **kwargs):
    return requests.get(
        f"{NESSUS_URL}{path}",
        headers=_headers(),
        verify=NESSUS_VERIFY_SSL,
        timeout=30,
        **kwargs,
    )


def _post(path, json_body=None):
    return requests.post(
        f"{NESSUS_URL}{path}",
        headers=_headers(),
        json=json_body or {},
        verify=NESSUS_VERIFY_SSL,
        timeout=30,
    )


def _find_template_uuid(template_name: str) -> str | None:
    resp = _get("/editor/policy/templates")
    resp.raise_for_status()
    for template in resp.json().get("templates", []):
        if template.get("name") == template_name:
            return template.get("uuid")
    return None


def _severity_label(severity_int: int) -> str:
    return {0: "Info", 1: "Low", 2: "Medium", 3: "High", 4: "Critical"}.get(
        severity_int, "Unknown"
    )


def scan_with_nessus(hostname: str) -> dict:
    if not _configured():
        return {
            "enabled": False,
            "error": (
                "Nessus is not configured. Set NESSUS_URL, NESSUS_ACCESS_KEY "
                "and NESSUS_SECRET_KEY in your environment to enable it."
            ),
        }

    try:
        template_uuid = _find_template_uuid(NESSUS_TEMPLATE_NAME)
        if not template_uuid:
            return {
                "enabled": True,
                "error": f"No Nessus scan template named '{NESSUS_TEMPLATE_NAME}' found",
                "findings": [],
            }

        create_resp = _post(
            "/scans",
            json_body={
                "uuid": template_uuid,
                "settings": {
                    "name": f"securelens-{hostname}-{int(time.time())}",
                    "text_targets": hostname,
                },
            },
        )
        create_resp.raise_for_status()
        scan_id = create_resp.json()["scan"]["id"]

        launch_resp = _post(f"/scans/{scan_id}/launch")
        launch_resp.raise_for_status()

        elapsed = 0
        status = "running"
        while elapsed < NESSUS_MAX_WAIT_SECONDS:
            details = _get(f"/scans/{scan_id}")
            details.raise_for_status()
            status = details.json().get("info", {}).get("status", "unknown")

            if status in ("completed", "aborted", "canceled", "empty"):
                break

            time.sleep(NESSUS_POLL_INTERVAL_SECONDS)
            elapsed += NESSUS_POLL_INTERVAL_SECONDS

        if status != "completed":
            return {
                "enabled": True,
                "target": hostname,
                "scan_id": scan_id,
                "error": f"Nessus scan ended with status '{status}' (may still be running)",
                "findings": [],
            }

        results = _get(f"/scans/{scan_id}")
        results.raise_for_status()
        vulns = results.json().get("vulnerabilities", [])

        findings = [
            {
                "plugin_id": v.get("plugin_id"),
                "name": v.get("plugin_name"),
                "severity": _severity_label(v.get("severity", 0)),
                "count": v.get("count"),
            }
            for v in vulns
            if v.get("severity", 0) > 0  # drop pure informational noise
        ]

        return {
            "enabled": True,
            "target": hostname,
            "scan_id": scan_id,
            "finding_count": len(findings),
            "findings": findings,
        }

    except requests.exceptions.RequestException as e:
        return {
            "enabled": True,
            "target": hostname,
            "error": f"Nessus API request failed: {e}",
            "findings": [],
        }


if __name__ == "__main__":
    target = input("Enter hostname: ").strip()
    import json
    print(json.dumps(scan_with_nessus(target), indent=4))
