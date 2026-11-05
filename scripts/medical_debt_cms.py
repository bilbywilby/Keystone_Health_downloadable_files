#!/usr/bin/env python3
"""
Medical Debt Case Management System

Workflow:
1. Load debts.json (or database table).
2. Compute due-dates relative to today (current date = 2026-11-05T04:39:50.895630-05:00)
3. Classify risk tier based on rules above.
4. Build action queues (CSV files) for each tier.
5. Dispatch work-orders to internal API using idempotency keys.
6. Append log entry with SHA-256 digest of each dispatched item.

Dependencies:
pip install requests cryptography python-dateutil
"""

import json
import csv
import hashlib
import hmac
import datetime as dt
from pathlib import Path
import os
import sys
import requests
from typing import Dict, List, Tuple

# ---------- CONFIGURATION ----------
DISPATCH_WEBHOOK_URL = os.getenv("DISPATCH_WEBHOOK_URL")
if not DISPATCH_WEBHOOK_URL:
    raise RuntimeError("DISPATCH_WEBHOOK_URL environment variable required")

LEDGER_ENC_KEY = os.getenv("LEDGER_ENC_KEY").encode("utf-8") if os.getenv("LEDGER_ENC_KEY") else b"placeholder-key-change-me"
HMAC_SECRET = LEDGER_ENC_KEY if LEDGER_ENC_KEY else b"default-secret"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------- HELPER FUNCTIONS ----------
def current_date():
    return dt.datetime.now(dt.timezone.utc)

def parse_datetime(s: str) -> dt.datetime:
    """Parse ISO string to UTC."""
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))

def compute_days_until(deadline_str: str) -> int:
    """Return days until deadline from now."""
    deadline = parse_datetime(deadline_str)
    return (deadline - current_date()).days

def redact_account_id(value: str) -> str:
    """Simple placeholder redaction for non-BAA channels."""
    if not value:
        return "REDACTED_ID"
    # In real PHI handling you'd use stronger methods (tokenization, hashing with key stored elsewhere)
    return f"ID-{hashlib.sha256(value.encode()).hexdigest()[:16]}"

def build_payload(account_id: str,
                 document_id: str,
                 violation_type: str,
                 deadline_str: str,
                 status: str) -> dict:
    """
    Construct the payload to be sent to the internal API.
    Keys must match what the receiving service expects.
    """
    account_id = redact_account_id(account_id)
    document_id = redact_account_id(document_id)
    return {
        "account_id": account_id,
        "document_id": document_id,
        "violation_type": violation_type,
        "action_deadline": deadline_str,
        "status": status,
        "source_timestamp": current_date().isoformat(),
        "idempotency_key": _idempotency_key(account_id, violation_type, deadline_str),
    }

def _idempotency_key(base: str, vtype: str, deadline: str) -> str:
    """Compute HMAC-SHA256 key used by the dispatcher script."""
    message = f"{base}|{vtype}|{deadline}"
    return hmac.new(HMAC_SECRET, message.encode("utf-8"), hashlib.sha256).hexdigest()

def post_with_retry(session: requests.Session,
                   url: str,
                   payload: dict,
                   max_retries: int = 3,
                   backoff: float = 2.0):
    """
    POST with exponential backoff, rate-limit aware.
    Returns True on success, False on failure after retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.post(url, json=payload, headers={"Idempotency-Key": _idempotency_key("dummy_base", "", "")})
            resp.raise_for_status()
            return True
        except requests.RequestException as exc:
            if attempt == max_retries:
                print(f"[ERROR] {exc} — giving up after {max_retries} attempts")
                return False
            wait = backoff * (attempt ** 2)
            print(f"[WARN] {exc} — retrying in {wait:.0f}s...")
            time.sleep(wait)
    return False

# ---------- DATA LOADING ----------
def load_debts(filepath: str = "data/debts.json") -> List[Dict]:
    """Load debt records from JSON file."""
    if not Path(filepath).exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_log(entry: Dict) -> None:
    """Append an event to the log with a SHA digest."""
    log_path = OUTPUT_DIR / "dispatch_log.txt"
    digest = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    log_line = f"{entry['account_id']},{entry['document_id']},{digest}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line)

# ---------- PRIORITY ALERT ENGINE ----------
def classify_risk(row: Dict) -> str:
    """
    Map violation type to tier based on regulatory requirements.
    """
    if row["violation_type"].startswith("Time-barred"):
        return "RED"
    elif row["violation_type"].startswith("501(r)"):
        return "RED"
    elif row["violation_type"].startswith("Upcoming"):
        return "YELLOW"
    else:
        return "GREEN"   # default catch-all

def main() -> int:
    debts = load_debts()
    if not debts:
        print("No debt records found.")
        return 0

    # --- 1. Sort by deadline ascending (earliest first)
    debts.sort(key=lambda x: parse_datetime(x["action_deadline"]))

    # --- 2. Build tiered CSV queues
    queues = {
        "RED": [],
        "YELLOW": [],
        "GREEN": [],
    }
    for d in debts:
        tier = classify_risk(d)
        queues[tier].append(d)

    # --- 3. Dispatch each queue
    session = requests.Session()

    successes = 0
    failures = 0

    for tier, items in queues.items():
        print(f"\n[{tier.upper()}]: {len(items)} pending")
        for item in items:
            # Redact identifiers before dispatch
            redacted_acc = redact_account_id(item["account_id"])
            redacted_doc = redact_account_id(item["document_id"])

            payload = build_payload(
                account_id=redacted_acc,
                document_id=redacted_doc,
                violation_type=item["violation_type"],
                deadline_str=item["action_deadline"],
                status=item["status"],
            )

            url = DISPATCH_WEBHOOK_URL
            if not url:
                print("[SKIP] No webhook URL configured — cannot dispatch.", file=sys.stderr)
                continue

            success = post_with_retry(session, url, payload)
            if success:
                successes += 1
                save_log(item)
                print(f"✅ Dispatched {item['account_id']} ({item['document_id']}) — {tier}")
            else:
                failures += 1
                print(f"❌ Failed to dispatch {item['account_id']} — {item['document_id']}", file=sys.stderr)

    print(f"\nDispatch Summary: {successes} succeeded, {failures} failed.")

    return failures

if __name__ == "__main__":
    sys.exit(main())
