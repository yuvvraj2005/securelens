import json
import concurrent.futures
from datetime import datetime

from backend.app.database.db import SessionLocal
from backend.app.database.models import ScanResult
from backend.app.core.config import SCAN_MAX_DURATION_SECONDS
from backend.app.core.logging_config import get_logger

from scanner.main_scanner import scan_website
from scanner.utils import UnsafeTargetError

logger = get_logger("scanner_service")

# Bounds how many scans run truly concurrently in-process. Each scan already
# shells out to nmap/nikto (which are themselves not free), so we don't want
# unbounded threads piling up under load.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def create_pending_scan(url: str, requested_by: str = "anonymous") -> ScanResult:
    """
    Insert a 'pending' row immediately and return it. The actual scan runs
    afterwards as a background task (see run_scan_job) — nmap/nikto/nessus
    can easily take minutes, so we never want an HTTP request blocked on
    them.
    """
    db = SessionLocal()
    try:
        scan_record = ScanResult(target=url, status="pending", requested_by=requested_by)
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)
        return scan_record
    finally:
        db.close()


def run_scan_job(scan_id: int, url: str) -> None:
    """Runs in a FastAPI BackgroundTask. Executes the full scan (with a
    hard wall-clock ceiling — SCAN_MAX_DURATION_SECONDS) and writes the
    result back to the row created by create_pending_scan."""
    db = SessionLocal()
    try:
        scan_record = db.query(ScanResult).filter(ScanResult.id == scan_id).first()
        if not scan_record:
            logger.warning("run_scan_job: scan id %s not found", scan_id)
            return

        scan_record.status = "running"
        db.commit()
        logger.info("scan %s started for target=%s", scan_id, url)

        future = _executor.submit(scan_website, url)

        try:
            result = future.result(timeout=SCAN_MAX_DURATION_SECONDS)

            scan_record.status = "completed"
            scan_record.score = result["score"]["overall_score"]
            scan_record.grade = result["score"]["grade"]
            scan_record.risk_level = result["score"]["risk_level"]
            scan_record.report = json.dumps(result)
            scan_record.completed_at = datetime.utcnow()
            logger.info("scan %s completed: score=%s grade=%s", scan_id,
                        scan_record.score, scan_record.grade)

        except concurrent.futures.TimeoutError:
            # Note: the underlying thread (and any subprocess it spawned)
            # is NOT forcibly killed here — Python can't safely kill a
            # thread mid-flight. nmap/nikto/nessus all have their own
            # internal timeouts (see their *_TIMEOUT_SECONDS env vars)
            # which bound the damage; this is a belt-and-suspenders cap
            # so a stuck job doesn't sit in 'running' forever.
            scan_record.status = "timed_out"
            scan_record.error = f"Scan exceeded the {SCAN_MAX_DURATION_SECONDS}s ceiling."
            scan_record.completed_at = datetime.utcnow()
            logger.warning("scan %s timed out after %ss", scan_id, SCAN_MAX_DURATION_SECONDS)

        except UnsafeTargetError as e:
            scan_record.status = "failed"
            scan_record.error = str(e)
            scan_record.completed_at = datetime.utcnow()

        except Exception as e:
            scan_record.status = "failed"
            scan_record.error = f"Unexpected error: {e}"
            scan_record.completed_at = datetime.utcnow()
            logger.exception("scan %s failed", scan_id)

        db.commit()
    finally:
        db.close()


def recover_stale_jobs() -> int:
    """Called on startup: any row still marked 'running' or 'pending' from
    before a restart is orphaned (no background task will ever finish it),
    so mark it failed rather than let it hang forever. Returns the count
    recovered."""
    db = SessionLocal()
    try:
        stale = (
            db.query(ScanResult)
            .filter(ScanResult.status.in_(["pending", "running"]))
            .all()
        )
        for scan in stale:
            scan.status = "failed"
            scan.error = "Scan interrupted by a server restart."
            scan.completed_at = datetime.utcnow()
        db.commit()
        return len(stale)
    finally:
        db.close()


def get_scan(scan_id: int):
    db = SessionLocal()
    try:
        scan = db.query(ScanResult).filter(ScanResult.id == scan_id).first()

        if not scan:
            return {"error": "Scan not found"}

        response = {
            "id": scan.id,
            "target": scan.target,
            "status": scan.status,
            "score": scan.score,
            "grade": scan.grade,
            "risk_level": scan.risk_level,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        }

        if scan.status in ("failed", "timed_out"):
            response["error"] = scan.error
        elif scan.status == "completed" and scan.report:
            response["report"] = json.loads(scan.report)

        return response
    finally:
        db.close()


def get_all_scans():
    db = SessionLocal()
    try:
        scans = db.query(ScanResult).order_by(ScanResult.id.desc()).all()

        return [
            {
                "id": scan.id,
                "target": scan.target,
                "status": scan.status,
                "score": scan.score,
                "grade": scan.grade,
                "risk_level": scan.risk_level,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
            }
            for scan in scans
        ]
    finally:
        db.close()


def get_scan_history(target: str):
    """All completed scans for one target, oldest first — the data behind
    a score-over-time chart on the frontend."""
    db = SessionLocal()
    try:
        scans = (
            db.query(ScanResult)
            .filter(ScanResult.target == target, ScanResult.status == "completed")
            .order_by(ScanResult.id.asc())
            .all()
        )

        return [
            {
                "id": scan.id,
                "score": scan.score,
                "grade": scan.grade,
                "risk_level": scan.risk_level,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            }
            for scan in scans
        ]
    finally:
        db.close()


def delete_scan(scan_id: int):
    db = SessionLocal()
    try:
        scan = db.query(ScanResult).filter(ScanResult.id == scan_id).first()

        if not scan:
            return {"error": "Scan not found"}

        db.delete(scan)
        db.commit()

        return {"message": f"Scan {scan_id} deleted successfully"}
    finally:
        db.close()
