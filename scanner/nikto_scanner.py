"""
Nikto integration.

Nikto (https://github.com/sullo/nikto) is a CLI web-server scanner. We shell
out to it with `-Format json` so we get structured output, and fall back to
a clear error object if the binary isn't installed or the scan fails/times
out. Nikto scans can take a while on a slow target, so we cap it with a
timeout and let the caller run it in a background job (see
backend/app/services/scanner_service.py).
"""

import json
import shutil
import subprocess
import tempfile
import os
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
                "Install it (see scripts/setup.sh) or set ENABLE_NIKTO=false."
            ),
        }

    hostname = urlparse(url).hostname or url

    with tempfile.NamedTemporaryFile(
        suffix=".json", delete=False
    ) as tmp:
        output_path = tmp.name

    try:
        subprocess.run(
            [
                binary,
                "-h", url,
                "-Format", "json",
                "-output", output_path,
                "-Tuning", "x6",   # skip the noisiest/DoS-prone tests
                "-ask", "no",
            ],
            capture_output=True,
            text=True,
            timeout=NIKTO_TIMEOUT_SECONDS,
        )

        findings = []
        try:
            with open(output_path, "r") as f:
                raw = json.load(f)
                for vuln in raw.get("vulnerabilities", []):
                    findings.append(
                        {
                            "id": vuln.get("id"),
                            "method": vuln.get("method"),
                            "url": vuln.get("url"),
                            "message": vuln.get("msg", vuln.get("message")),
                        }
                    )
        except (json.JSONDecodeError, FileNotFoundError):
            # Nikto sometimes writes nothing if it found zero issues
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
            "error": f"nikto scan exceeded {NIKTO_TIMEOUT_SECONDS}s timeout",
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
