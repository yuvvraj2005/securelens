from datetime import datetime

from backend.app.database.db import SessionLocal
from backend.app.database.models import AuditLog


def log_event(target: str, action: str, api_key: str = None, source_ip: str = None, detail: str = None):
    db = SessionLocal()
    try:
        entry = AuditLog(
            timestamp=datetime.utcnow(),
            api_key=api_key,
            source_ip=source_ip,
            target=target,
            action=action,
            detail=detail,
        )
        db.add(entry)
        db.commit()
    finally:
        db.close()


def get_audit_log(limit: int = 200):
    db = SessionLocal()
    try:
        entries = (
            db.query(AuditLog)
            .order_by(AuditLog.id.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "api_key": e.api_key,
                "source_ip": e.source_ip,
                "target": e.target,
                "action": e.action,
                "detail": e.detail,
            }
            for e in entries
        ]
    finally:
        db.close()
