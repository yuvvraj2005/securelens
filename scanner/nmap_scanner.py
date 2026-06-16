import subprocess
import json
from urllib.parse import urlparse


def scan_ports(url):

    try:

        hostname = urlparse(url).netloc

        if not hostname:
            hostname = url

        result = subprocess.run(
            [
                "nmap",
                "-F",
                hostname
            ],
            capture_output=True,
            text=True
        )

        ports = []

        for line in result.stdout.splitlines():

            if "/tcp" in line and "open" in line:

                parts = line.split()

                ports.append(
                    {
                        "port": parts[0].split("/")[0],
                        "service": parts[2]
                    }
                )

        return {
            "target": hostname,
            "open_ports": ports
        }


    except Exception as e:

        return {
            "error": str(e)
        }


if __name__ == "__main__":

    url = input("Enter URL: ")

    result = scan_ports(url)

    print(
        json.dumps(
            result,
            indent=4
        )
    )
