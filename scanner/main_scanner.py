from scanner.header_scanner import scan_headers
from scanner.ssl_scanner import get_ssl_info
from scanner.score_engine import calculate_score
from scanner.tech_detector import detect_technology
from scanner.nmap_scanner import scan_ports
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

    # Run scanners
    header_results = scan_headers(normalized_url)

    ssl_results = get_ssl_info(normalized_url)

    technology_results = detect_technology(
        normalized_url
    )

    nmap_results = scan_ports(
        normalized_url
    )


    # Calculate overall score
    score_results = calculate_score(
        header_results,
        ssl_results,
        nmap_results
    )

    report = {
        "target": normalized_url,
        "score": score_results,
        "headers": header_results,
        "ssl": ssl_results,
        "technology": technology_results,
        "nmap": nmap_results
    }

    return report

if __name__ == "__main__":

    url = input("Enter URL: ").strip()

    report = scan_website(url)

    print("\n=== SECURELENS REPORT ===\n")

    print(json.dumps(report, indent=4))
