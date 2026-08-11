"""
Centralized environment configuration. Reads from a .env file (see
.env.example at the repo root) via python-dotenv so nothing here needs to
be hardcoded or committed.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///securelens.db")

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

# --- Scanner toggles ---
ENABLE_NMAP = os.getenv("ENABLE_NMAP", "true").lower() == "true"
ENABLE_NIKTO = os.getenv("ENABLE_NIKTO", "true").lower() == "true"
ENABLE_NESSUS = os.getenv("ENABLE_NESSUS", "false").lower() == "true"

# --- Auth ---
# Comma-separated list of accepted API keys. Empty = auth disabled (fine for
# local dev, NOT fine for anything reachable over a network).
API_KEYS = {
    key.strip()
    for key in os.getenv("API_KEYS", "").split(",")
    if key.strip()
}
AUTH_ENABLED = len(API_KEYS) > 0

# --- Rate limiting (in-memory, per API key / IP; single-process only —
#     see docs/architecture.md for the Redis-backed multi-instance note) ---
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_SCANS_PER_HOUR = int(os.getenv("RATE_LIMIT_SCANS_PER_HOUR", "10"))

# --- Target ownership verification ---
# When true, /scan refuses to run against a target until it's been proven
# via DNS TXT record or well-known file (see backend/app/services/verification_service.py).
# Off by default so local/demo use isn't blocked; turn it on for anything
# publicly reachable.
REQUIRE_TARGET_VERIFICATION = os.getenv("REQUIRE_TARGET_VERIFICATION", "false").lower() == "true"

# --- Scan safety ceiling ---
# Hard wall-clock cap on a single scan job, independent of each tool's own
# internal timeout. Prevents one hung scanner from leaving a DB row stuck
# in 'running' forever.
SCAN_MAX_DURATION_SECONDS = int(os.getenv("SCAN_MAX_DURATION_SECONDS", "900"))

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
