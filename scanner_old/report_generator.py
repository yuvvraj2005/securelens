def generate_report(scan_result):

    report = []

    report.append("=" * 50)
    report.append("SECURELENS SECURITY REPORT")
    report.append("=" * 50)

    report.append(f"\nTarget: {scan_result['target']}")

    score = scan_result["score"]

    report.append(
        f"\nOverall Score: {score['overall_score']}/100"
    )

    report.append(
        f"Grade: {score['grade']}"
    )

    report.append(
        f"Risk Level: {score['risk_level']}"
    )

    # SSL Information
    ssl = scan_result["ssl"]

    report.append("\nSSL INFORMATION")
    report.append("-" * 20)

    report.append(
        f"SSL Enabled: {ssl.get('ssl_enabled', False)}"
    )

    report.append(
        f"Issuer: {ssl.get('issuer', 'Unknown')}"
    )

    report.append(
        f"Expires On: {ssl.get('expires_on', 'Unknown')}"
    )

    # Technology Information
    tech = scan_result.get("technology", {})

    report.append("\nTECHNOLOGY DETECTED")
    report.append("-" * 20)

    report.append(
        f"Server: {tech.get('server', 'Unknown')}"
    )

    report.append(
        f"Framework: {tech.get('framework', 'Unknown')}"
    )

    report.append(
        f"CDN: {tech.get('cdn', 'Unknown')}"
    )

    # Findings
    findings = scan_result["headers"].get(
        "findings",
        []
    )

    report.append("\nFINDINGS")
    report.append("-" * 20)

    if not findings:
        report.append(
            "No missing security headers detected."
        )

    else:
        for finding in findings:

            report.append(
                f"[{finding['severity']}] "
                f"{finding['title']}"
            )

    return "\n".join(report)
