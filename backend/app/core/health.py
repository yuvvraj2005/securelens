"""Backing logic for GET /health — reports what's actually usable right
now (scanner binaries found, Nessus reachable, DB reachable) rather than
just 'the process is alive'. Useful for a status page and for debugging
deploys where e.g. nikto didn't get installed in the image."""

import shutil
import requests
from sqlalchemy import text

from backend.app.core.config import ENABLE_NMAP, ENABLE_NIKTO, ENABLE_NESSUS
from backend.app.database.db import SessionLocal
from scanner.nessus_scanner import NESSUS_URL, _configured as nessus_configured


def check_database() -> dict:
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_nmap() -> dict:
    if not ENABLE_NMAP:
        return {"enabled": False}
    return {"enabled": True, "installed": shutil.which("nmap") is not None}


def check_nikto() -> dict:
    if not ENABLE_NIKTO:
        return {"enabled": False}
    found = shutil.which("nikto") or shutil.which("nikto.pl")
    return {"enabled": True, "installed": found is not None}


def check_nessus() -> dict:
    if not ENABLE_NESSUS:
        return {"enabled": False}

    if not nessus_configured():
        return {"enabled": True, "configured": False}

    try:
        resp = requests.get(f"{NESSUS_URL}/server/status", timeout=5, verify=False)
        return {"enabled": True, "configured": True, "reachable": resp.status_code == 200}
    except requests.exceptions.RequestException as e:
        return {"enabled": True, "configured": True, "reachable": False, "error": str(e)}


def get_health() -> dict:
    checks = {
        "database": check_database(),
        "nmap": check_nmap(),
        "nikto": check_nikto(),
        "nessus": check_nessus(),
    }

    healthy = checks["database"]["ok"] and (
        not checks["nmap"]["enabled"] or checks["nmap"]["installed"]
    ) and (
        not checks["nikto"]["enabled"] or checks["nikto"]["installed"]
    )

    return {"status": "ok" if healthy else "degraded", "checks": checks}
