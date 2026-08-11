from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ScanResult(Base):

    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)

    target = Column(String, index=True)

    # pending -> running -> completed | failed | timed_out
    status = Column(String, default="pending", index=True)

    requested_by = Column(String, nullable=True)  # API key / 'anonymous'

    score = Column(Integer, nullable=True)
    grade = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)

    error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    report = Column(Text, nullable=True)


class AuditLog(Base):
    """Every scan request gets a row here, independent of whether the scan
    itself succeeded — this is the accountability trail for a tool that
    runs nmap/nikto/nessus against third-party infrastructure."""

    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    api_key = Column(String, nullable=True, index=True)
    source_ip = Column(String, nullable=True)
    target = Column(String, index=True)
    action = Column(String)  # e.g. 'scan_requested', 'scan_rejected'
    detail = Column(Text, nullable=True)


class TargetVerification(Base):
    """Tracks the ownership-verification flow for a target: a token is
    issued, the caller proves control of the domain (DNS TXT record or a
    well-known file), and the target is marked verified. See
    verification_service.py."""

    __tablename__ = "target_verifications"

    id = Column(Integer, primary_key=True, index=True)

    hostname = Column(String, index=True)
    token = Column(String)
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
