import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.core.config import ALLOWED_ORIGINS, REQUIRE_TARGET_VERIFICATION, AUTH_ENABLED
from backend.app.core.logging_config import setup_logging, get_logger
from backend.app.core.security import require_api_key, enforce_rate_limit
from backend.app.core.health import get_health
from backend.app.services.scanner_service import (
    create_pending_scan,
    run_scan_job,
    recover_stale_jobs,
    get_scan,
    get_all_scans,
    get_scan_history,
    delete_scan,
)
from backend.app.services.audit_service import log_event, get_audit_log
from backend.app.services.verification_service import (
    start_verification,
    check_verification,
    is_target_verified,
)
from scanner.utils import normalize_url, extract_hostname, assert_public_target, UnsafeTargetError
from scanner.report_export import generate_html_report, generate_pdf_report

setup_logging()
logger = get_logger("main")

app = FastAPI(
    title="SecureLens API",
    version="0.3.0",
    description=(
        "AI-assisted website security auditing platform. Orchestrates "
        "header/SSL/tech checks plus nmap, nikto and (optionally) Nessus."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    recovered = recover_stale_jobs()
    if recovered:
        logger.warning("recovered %s stale scan job(s) after restart", recovered)
    if not AUTH_ENABLED:
        logger.warning(
            "AUTH IS DISABLED (no API_KEYS configured). Fine for local dev; "
            "set API_KEYS in .env before exposing this publicly."
        )


class ScanRequest(BaseModel):
    url: str
    # Requiring an explicit ownership/authorization confirmation is a
    # standard guardrail for any tool that runs nmap/nikto/nessus against a
    # user-supplied target. This is honesty-based; for an enforced version
    # see REQUIRE_TARGET_VERIFICATION + the /verify endpoints below.
    authorized: bool = Field(
        ...,
        description="Must be true — confirms the caller owns or has explicit permission to scan this target.",
    )


class VerifyStartRequest(BaseModel):
    hostname: str


@app.get("/")
def root():
    return {"message": "SecureLens API Running"}


@app.get("/health")
def health():
    return get_health()


@app.post("/scan", status_code=202)
def scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    api_key: str = Depends(require_api_key),
):
    enforce_rate_limit(http_request, api_key)

    source_ip = http_request.client.host if http_request.client else None

    if not request.authorized:
        log_event(request.url, "scan_rejected", api_key, source_ip, "authorized=false")
        raise HTTPException(
            status_code=400,
            detail="You must confirm you own or have explicit permission to scan this target.",
        )

    normalized = normalize_url(request.url)

    try:
        hostname = extract_hostname(normalized)
        assert_public_target(hostname)
    except UnsafeTargetError as e:
        log_event(normalized, "scan_rejected", api_key, source_ip, str(e))
        raise HTTPException(status_code=400, detail=str(e))

    if REQUIRE_TARGET_VERIFICATION and not is_target_verified(hostname):
        log_event(normalized, "scan_rejected", api_key, source_ip, "target not verified")
        raise HTTPException(
            status_code=403,
            detail=(
                f"'{hostname}' has not completed ownership verification. "
                f"POST /verify/start with this hostname, then GET /verify/check/{{id}}."
            ),
        )

    log_event(normalized, "scan_requested", api_key, source_ip)

    scan_record = create_pending_scan(normalized, requested_by=api_key)
    background_tasks.add_task(run_scan_job, scan_record.id, normalized)

    return {
        "scan_id": scan_record.id,
        "status": "pending",
        "message": "Scan started. Poll GET /scan/{scan_id} for status and results.",
    }


@app.get("/scan/{scan_id}")
def get_saved_scan(scan_id: int, api_key: str = Depends(require_api_key)):
    result = get_scan(scan_id)
    if "error" in result and result["error"] == "Scan not found":
        raise HTTPException(status_code=404, detail="Scan not found")
    return result


@app.get("/scan/{scan_id}/export")
def export_scan(scan_id: int, format: str = "json", api_key: str = Depends(require_api_key)):
    result = get_scan(scan_id)
    if "error" in result and result["error"] == "Scan not found":
        raise HTTPException(status_code=404, detail="Scan not found")
    if result.get("status") != "completed":
        raise HTTPException(status_code=409, detail=f"Scan is '{result.get('status')}', not completed yet.")

    report = result["report"]

    if format == "json":
        return report

    if format == "html":
        return Response(content=generate_html_report(report), media_type="text/html")

    if format == "pdf":
        pdf_bytes = generate_pdf_report(report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=securelens-scan-{scan_id}.pdf"},
        )

    raise HTTPException(status_code=400, detail="format must be one of: json, html, pdf")


@app.get("/scans")
def list_scans(api_key: str = Depends(require_api_key)):
    return get_all_scans()


@app.get("/scans/history")
def scan_history(target: str, api_key: str = Depends(require_api_key)):
    """Score-over-time for a single target — feeds a trend chart on the frontend."""
    return get_scan_history(normalize_url(target))


@app.delete("/scan/{scan_id}")
def remove_scan(scan_id: int, api_key: str = Depends(require_api_key)):
    result = delete_scan(scan_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/verify/start")
def verify_start(request: VerifyStartRequest, api_key: str = Depends(require_api_key)):
    return start_verification(request.hostname)


@app.get("/verify/check/{verification_id}")
def verify_check(verification_id: int, api_key: str = Depends(require_api_key)):
    result = check_verification(verification_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/audit-log")
def audit_log(limit: int = 200, api_key: str = Depends(require_api_key)):
    return get_audit_log(limit)
