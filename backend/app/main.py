from fastapi import FastAPI
from pydantic import BaseModel

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from scanner.main_scanner import scan_website

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

    result = scan_website(
        request.url
    )

    return result
