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

    report.append("\nHEADER FINDINGS")
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

    # Open ports (nmap)
    nmap = scan_result.get("nmap", {})
    open_ports = nmap.get("open_ports", [])

    report.append("\nOPEN PORTS (nmap)")
    report.append("-" * 20)

    if not nmap.get("enabled", True):
        report.append("nmap scan disabled/unavailable.")
    elif not open_ports:
        report.append("No open ports detected (or scan failed).")
    else:
        for p in open_ports:
            report.append(
                f"{p['port']}/tcp {p['state']} {p['service']} {p.get('version', '')}"
            )

    # Nikto findings
    nikto = scan_result.get("nikto", {})

    report.append("\nWEB SERVER FINDINGS (nikto)")
    report.append("-" * 20)

    if not nikto.get("enabled", True):
        report.append(nikto.get("error", "nikto scan disabled/unavailable."))
    elif nikto.get("error"):
        report.append(f"Error: {nikto['error']}")
    elif not nikto.get("findings"):
        report.append("No issues reported by nikto.")
    else:
        for f in nikto["findings"]:
            report.append(f"- {f.get('message', f)}")

    # Nessus findings
    nessus = scan_result.get("nessus", {})

    report.append("\nVULNERABILITY SCAN (nessus)")
    report.append("-" * 20)

    if not nessus.get("enabled", True):
        report.append(nessus.get("error", "Nessus not configured."))
    elif nessus.get("error"):
        report.append(f"Error: {nessus['error']}")
    elif not nessus.get("findings"):
        report.append("No vulnerabilities reported by Nessus.")
    else:
        for f in nessus["findings"]:
            report.append(f"[{f.get('severity')}] {f.get('name')}")

    return "\n".join(report)
