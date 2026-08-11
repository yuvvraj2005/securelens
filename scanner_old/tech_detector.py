import requests


def detect_technology(url):

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )

        headers = response.headers


        technologies = {
            "server": "Unknown",
            "framework": "Unknown",
            "cdn": "Unknown"
        }

        # Detect Server
        if "Server" in headers:
            technologies["server"] = headers["Server"]

        # Detect Framework
        if "X-Powered-By" in headers:
            technologies["framework"] = headers["X-Powered-By"]

        # Detect Cloudflare
        if "CF-RAY" in headers:
            technologies["cdn"] = "Cloudflare"

        elif "x-amz-cf-id" in headers:
            technologies["cdn"] = "CloudFront"

        elif "akamai" in str(headers).lower():
            technologies["cdn"] = "Akamai"

        html = response.text.lower()

        # Detect WordPress
        if "wp-content" in html:
            technologies["framework"] = "WordPress"

        # Detect Next.js
        elif "_next/static" in html:
            technologies["framework"] = "Next.js"


        # Detect React
        elif "__next" in html:
            technologies["framework"] = "Next.js"

        elif "react" in html:
            technologies["framework"] = "React"

        # Detect Angular
        elif "ng-version" in html:
            technologies["framework"] = "Angular"

        return technologies

    except Exception as e:

        return {
            "error": str(e)
        }


if __name__ == "__main__":

    url = input("Enter URL: ").strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = detect_technology(url)

    print("\n=== Technology Detection ===\n")

    for key, value in result.items():
        print(f"{key}: {value}")
