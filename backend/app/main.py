from fastapi import FastAPI
from pydantic import BaseModel

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
    return {
        "status": "received",
        "target": request.url
    }
