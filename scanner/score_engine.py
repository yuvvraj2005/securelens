def calculate_score(
    header_report,
    ssl_report,
    nmap_report
):

    score = 0

    # Header score contributes up to 70 points
    header_score = header_report.get("score", 0)
    score += int(header_score * 0.7)

    # SSL contributes up to 30 points
    if ssl_report.get("ssl_enabled"):
        score += 20

        days_remaining = ssl_report.get("days_remaining", 0)

        if days_remaining > 90:
            score += 10
        elif days_remaining > 30:
            score += 5

    # Grade
    if score >= 90:
        grade = "A"
        risk = "Low"

    elif score >= 80:
        grade = "B"
        risk = "Low"

    elif score >= 70:
        grade = "C"
        risk = "Medium"

    elif score >= 60:
        grade = "D"
        risk = "High"

    else:
        grade = "F"
        risk = "Critical"

    return {
        "overall_score": score,
        "grade": grade,
        "risk_level": risk
    }
