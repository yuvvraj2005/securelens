from header_scanner import scan_headers
from ssl_scanner import get_ssl_info
import json


def normalize_url(url):
    """
    Ensure the URL has a scheme.
    Example:
        github.com -> https://github.com
    """
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def scan_website(url):
    normalized_url = normalize_url(url)

    header_results = scan_headers(normalized_url)

    ssl_results = get_ssl_info(normalized_url)

    report = {
        "target": normalized_url,
        "headers": header_results,
        "ssl": ssl_results
    }

    return report


if __name__ == "__main__":
    url = input("Enter URL: ").strip()

    report = scan_website(url)

    print("\n=== SECURELENS REPORT ===\n")
    print(json.dumps(report, indent=4))
