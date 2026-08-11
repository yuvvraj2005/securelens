"""
Target ownership verification.

The `authorized: true` flag on /scan is honesty-based — it stops accidental
misuse but nothing stops someone from just checking the box for a site they
don't own. This module adds an enforceable alternative: prove control of
the domain the same way Google Search Console / Let's Encrypt / countless
SaaS products do —

  1. Caller starts verification for a hostname -> gets a random token and
     two ways to prove it:
       a) DNS TXT record:  _securelens-verify.<hostname>  =  <token>
       b) HTTP file:       http(s)://<hostname>/.well-known/securelens-verify.txt
          containing exactly the token
  2. Caller places the token, then calls check -> we look for either proof.
  3. Once verified, that hostname can be scanned even when
     REQUIRE_TARGET_VERIFICATION=true.

DNS TXT lookup uses dnspython if it's installed; if not, only the
well-known-file method is available (a warning is included in the
response rather than failing hard).
"""

import secrets
import requests

from backend.app.database.db import SessionLocal
from backend.app.database.models import TargetVerification

WELL_KNOWN_PATH = "/.well-known/securelens-verify.txt"
DNS_PREFIX = "_securelens-verify"


def start_verification(hostname: str) -> dict:
    token = secrets.token_hex(16)

    db = SessionLocal()
    try:
        record = TargetVerification(hostname=hostname, token=token, verified=False)
        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "verification_id": record.id,
            "hostname": hostname,
            "token": token,
            "instructions": {
                "dns_txt": f"Create a TXT record at {DNS_PREFIX}.{hostname} with value: {token}",
                "well_known_file": (
                    f"Serve a file at https://{hostname}{WELL_KNOWN_PATH} "
                    f"whose contents are exactly: {token}"
                ),
            },
        }
    finally:
        db.close()


def _check_well_known(hostname: str, token: str) -> bool:
    for scheme in ("https", "http"):
        try:
            resp = requests.get(
                f"{scheme}://{hostname}{WELL_KNOWN_PATH}",
                timeout=10,
            )
            if resp.status_code == 200 and resp.text.strip() == token:
                return True
        except requests.exceptions.RequestException:
            continue
    return False


def _check_dns_txt(hostname: str, token: str) -> tuple[bool, str | None]:
    try:
        import dns.resolver  # optional dependency
    except ImportError:
        return False, "dnspython not installed — only well-known-file check was attempted"

    try:
        answers = dns.resolver.resolve(f"{DNS_PREFIX}.{hostname}", "TXT")
        for rdata in answers:
            value = b"".join(rdata.strings).decode("utf-8", errors="ignore")
            if value == token:
                return True, None
    except Exception:
        pass

    return False, None


def check_verification(verification_id: int) -> dict:
    db = SessionLocal()
    try:
        record = (
            db.query(TargetVerification)
            .filter(TargetVerification.id == verification_id)
            .first()
        )

        if not record:
            return {"error": "Verification request not found"}

        if record.verified:
            return {"verification_id": record.id, "hostname": record.hostname, "verified": True}

        via_file = _check_well_known(record.hostname, record.token)
        via_dns, dns_note = _check_dns_txt(record.hostname, record.token)

        if via_file or via_dns:
            from datetime import datetime
            record.verified = True
            record.verified_at = datetime.utcnow()
            db.commit()

            return {
                "verification_id": record.id,
                "hostname": record.hostname,
                "verified": True,
                "method": "well_known_file" if via_file else "dns_txt",
            }

        return {
            "verification_id": record.id,
            "hostname": record.hostname,
            "verified": False,
            "note": dns_note,
        }
    finally:
        db.close()


def is_target_verified(hostname: str) -> bool:
    db = SessionLocal()
    try:
        record = (
            db.query(TargetVerification)
            .filter(
                TargetVerification.hostname == hostname,
                TargetVerification.verified == True,  # noqa: E712
            )
            .first()
        )
        return record is not None
    finally:
        db.close()
