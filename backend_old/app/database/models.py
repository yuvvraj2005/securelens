from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


class ScanResult(Base):

    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)

    target = Column(String)

    score = Column(Integer)

    grade = Column(String)

    risk_level = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    report = Column(Text)
