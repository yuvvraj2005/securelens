from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.services.scanner_service import (
    run_scan,
    get_scan
)

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

app = FastAPI(
    title="SecureLens API",
    version="0.1.0"
)


class ScanRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {
        "message": "SecureLens API Running"
    }


@app.post("/scan")
def scan(request: ScanRequest):

    return run_scan(
        request.url
    )


@app.get("/scan/{scan_id}")
def get_saved_scan(scan_id: int):

    return get_scan(scan_id)
