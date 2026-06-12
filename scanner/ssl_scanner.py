import ssl
import socket
from datetime import datetime
from urllib.parse import urlparse


def get_ssl_info(url):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        hostname = urlparse(url).hostname

        context = ssl.create_default_context()

        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:

                cert = ssock.getpeercert()

                issuer = dict(x[0] for x in cert["issuer"])
                subject = dict(x[0] for x in cert["subject"])

                expiry_date = datetime.strptime(
                    cert["notAfter"],
                    "%b %d %H:%M:%S %Y %Z"
                )

                days_remaining = (expiry_date - datetime.now()).days

                return {
                    "domain": hostname,
                    "ssl_enabled": True,
                    "issuer": issuer.get("organizationName", "Unknown"),
                    "subject": subject.get("commonName", "Unknown"),
                    "expires_on": expiry_date.strftime("%Y-%m-%d"),
                    "days_remaining": days_remaining
                }

    except Exception as e:
        return {
            "domain": url,
            "ssl_enabled": False,
            "error": str(e)
        }


if __name__ == "__main__":

    url = input("Enter URL: ").strip()

    result = get_ssl_info(url)

    print("\n=== SSL Analysis ===\n")

    for key, value in result.items():
        print(f"{key}: {value}")
