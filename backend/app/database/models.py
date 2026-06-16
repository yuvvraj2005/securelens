from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text


class Base(DeclarativeBase):
    pass


class ScanResult(Base):

    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)

    target = Column(String)

    score = Column(Integer)

    report = Column(Text)
