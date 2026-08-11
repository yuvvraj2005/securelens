"""
Nikto integration.

Nikto is a CLI web-server scanner. We shell out to it with JSON output
and convert the results into the SecureLens report format.
"""

import json
import os
import shutil
import subprocess
import tempfile
from urllib.parse import urlparse

NIKTO_TIMEOUT_SECONDS = int(os.getenv("NIKTO_TIMEOUT_SECONDS", "300"))


def _nikto_binary():
    return shutil.which("nikto") or shutil.which("nikto.pl")


def scan_with_nikto(url: str) -> dict:
    binary = _nikto_binary()

    if not binary:
        return {
            "enabled": False,
            "error": (
                "nikto is not installed or not on PATH. "
                "Install it or set ENABLE_NIKTO=false."
            ),
        }

    hostname = urlparse(url).hostname or url

    with tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False,
    ) as tmp:
        output_path = tmp.name

    try:
        subprocess.run(
            [
                binary,
                "-h",
                url,
                "-Format",
                "json",
                "-output",
                output_path,
                "-Tuning",
                "x6",
                "-ask",
                "no",
            ],
            capture_output=True,
            text=True,
            timeout=NIKTO_TIMEOUT_SECONDS,
        )

        findings = []

        try:
            with open(output_path, "r") as f:
                raw = json.load(f)

            if isinstance(raw, dict):
                vulnerabilities = raw.get("vulnerabilities", [])
            elif isinstance(raw, list):
                vulnerabilities = raw
            else:
                vulnerabilities = []

            for vuln in vulnerabilities:
                if not isinstance(vuln, dict):
                    continue

                findings.append(
                    {
                        "id": vuln.get("id"),
                        "method": vuln.get("method"),
                        "url": vuln.get("url"),
                        "message": vuln.get(
                            "msg",
                            vuln.get("message"),
                        ),
                    }
                )

        except (json.JSONDecodeError, FileNotFoundError):
            findings = []

        return {
            "enabled": True,
            "target": hostname,
            "finding_count": len(findings),
            "findings": findings,
        }

    except subprocess.TimeoutExpired:
        return {
            "enabled": True,
            "target": hostname,
            "error": (
                f"nikto scan exceeded "
                f"{NIKTO_TIMEOUT_SECONDS}s timeout"
            ),
            "findings": [],
        }

    except Exception as e:
        return {
            "enabled": True,
            "target": hostname,
            "error": str(e),
            "findings": [],
        }

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


if __name__ == "__main__":
    target = input("Enter URL: ").strip()
    print(json.dumps(scan_with_nikto(target), indent=4))