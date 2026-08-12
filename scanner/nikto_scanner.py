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


NIKTO_TIMEOUT_SECONDS = int(
    os.getenv("NIKTO_TIMEOUT_SECONDS", "300")
)


def _nikto_binary():
    """Find the Nikto executable."""
    return shutil.which("nikto") or shutil.which("nikto.pl")


def scan_with_nikto(url: str) -> dict:
    """Run Nikto against a target URL and return structured results."""

    binary = _nikto_binary()

    if not binary:
        return {
            "enabled": False,
            "error": (
                "nikto is not installed or not on PATH. "
                "Install it or set ENABLE_NIKTO=false."
            ),
            "findings": [],
        }

    hostname = urlparse(url).hostname or url

    with tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False,
    ) as tmp:
        output_path = tmp.name

    try:
        # Run Nikto
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

        # Parse Nikto JSON output
        try:
            with open(output_path, "r") as f:
                raw = json.load(f)

            # Nikto may return either a dictionary containing
            # vulnerabilities or a list of vulnerability objects.
            if isinstance(raw, dict):
                vulnerabilities = raw.get(
                    "vulnerabilities",
                    [],
                )
            elif isinstance(raw, list):
                vulnerabilities = raw
            else:
                vulnerabilities = []

            for vuln in vulnerabilities:

                # Ignore anything that isn't a dictionary.
                if not isinstance(vuln, dict):
                    continue

                # Nikto normally uses "msg".
                # Some versions/output formats may use "message".
                message = (
                    vuln.get("msg")
                    or vuln.get("message")
                )

                # Do not create fake findings containing
                # null values.
                if not message:
                    continue

                findings.append(
                    {
                        "id": vuln.get("id"),
                        "method": vuln.get("method"),
                        "url": vuln.get("url"),
                        "message": message,
                    }
                )

        except (
            json.JSONDecodeError,
            FileNotFoundError,
        ):
            # Nikto may produce no JSON file when there
            # are no findings.
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
        # Always remove the temporary JSON file.
        if os.path.exists(output_path):
            os.remove(output_path)


if __name__ == "__main__":
    target = input("Enter URL: ").strip()

    result = scan_with_nikto(target)

    print(
        json.dumps(
            result,
            indent=4,
        )
    )