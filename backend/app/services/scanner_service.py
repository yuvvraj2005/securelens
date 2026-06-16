import json

from backend.app.database.db import SessionLocal
from backend.app.database.models import ScanResult

from scanner.main_scanner import scan_website


def run_scan(url):

    result = scan_website(url)

    db = SessionLocal()

    scan_record = ScanResult(
        target=result["target"],
        score=result["score"]["overall_score"],
        report=json.dumps(result)
    )

    db.add(scan_record)

    db.commit()

    db.refresh(scan_record)

    db.close()

    return {
        "scan_id": scan_record.id,
        "result": result
    }

def get_scan(scan_id):

    db = SessionLocal()

    scan = (
        db.query(ScanResult)
        .filter(ScanResult.id == scan_id)
        .first()
    )

    db.close()

    if not scan:
        return {
            "error": "Scan not found"
        }

    return {
        "id": scan.id,
        "target": scan.target,
        "score": scan.score,
        "report": json.loads(scan.report)
    }

def get_all_scans():

    db = SessionLocal()

    scans = db.query(ScanResult).all()

    db.close()

    return [
        {
            "id": scan.id,
            "target": scan.target,
            "score": scan.score
        }
        for scan in scans
    ]
