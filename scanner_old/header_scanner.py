import requests
import json

SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "penalty": 15,
        "severity": "High"
    },
    "Strict-Transport-Security": {
        "penalty": 10,
        "severity": "Medium"
    },
    "X-Frame-Options": {
        "penalty": 10,
        "severity": "Medium"
    },
    "X-Content-Type-Options": {
        "penalty": 10,
        "severity": "Medium"
    },
    "Referrer-Policy": {
        "penalty": 5,
        "severity": "Low"
    }
}


def scan_headers(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )

        score = 100
        findings = []

        for header, config in SECURITY_HEADERS.items():

            if header not in response.headers:

                score -= config["penalty"]

                findings.append({
                    "severity": config["severity"],
                    "title": f"Missing {header}",
                    "description": f"The website does not send the {header} security header."
                })

        report = {
            "url": url,
            "status_code": response.status_code,
            "score": max(score, 0),
            "findings": findings
        }

        return report

    except requests.exceptions.RequestException as e:

        return {
            "url": url,
            "error": str(e)
        }


def print_report(report):

    print("\n" + "=" * 50)
    print("SECURELENS HEADER SCAN REPORT")
    print("=" * 50)

    if "error" in report:
        print(f"\nError: {report['error']}")
        return

    print(f"\nURL: {report['url']}")
    print(f"Status Code: {report['status_code']}")
    print(f"Security Score: {report['score']}/100")

    print("\nFindings:")

    if not report["findings"]:
        print("✅ No missing security headers detected.")

    else:
        for finding in report["findings"]:
            print(
                f"\n[{finding['severity']}] {finding['title']}"
            )
            print(f"  {finding['description']}")

    print("\nJSON Output:")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":

    url = input("Enter URL: ").strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    report = scan_headers(url)

    print_report(report)
