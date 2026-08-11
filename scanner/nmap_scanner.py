import subprocess
import json
import os
import shutil
from urllib.parse import urlparse

NMAP_TIMEOUT_SECONDS = int(os.getenv("NMAP_TIMEOUT_SECONDS", "120"))


def scan_ports(url):
    try:
        if not shutil.which("nmap"):
            return {
                "enabled": False,
                "error": "nmap is not installed or not on PATH. See scripts/setup.sh.",
                "open_ports": [],
            }

        hostname = urlparse(url).netloc or urlparse(url).hostname or url
        # strip any port/userinfo that may have leaked into netloc
        hostname = hostname.split("@")[-1].split(":")[0]

        result = subprocess.run(
            ["nmap", "-F", "-sV", hostname],
            capture_output=True,
            text=True,
            timeout=NMAP_TIMEOUT_SECONDS,
        )

        ports = []

        for line in result.stdout.splitlines():
            if "/tcp" in line and "open" in line:
                parts = line.split()
                ports.append(
                    {
                        "port": parts[0].split("/")[0],
                        "state": parts[1],
                        "service": parts[2],
                        "version": " ".join(parts[3:]) if len(parts) > 3 else "Unknown",
                    }
                )

        return {
            "enabled": True,
            "target": hostname,
            "open_ports": ports,
        }

    except subprocess.TimeoutExpired:
        return {
            "enabled": True,
            "error": f"nmap scan exceeded {NMAP_TIMEOUT_SECONDS}s timeout",
            "open_ports": [],
        }
    except Exception as e:
        return {
            "enabled": True,
            "error": str(e),
            "open_ports": [],
        }


if __name__ == "__main__":
    url = input("Enter URL: ")
    result = scan_ports(url)
    print(json.dumps(result, indent=4))
