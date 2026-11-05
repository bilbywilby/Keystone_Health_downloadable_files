import csv
import hashlib
import hmac
import json
import os
import sys
import time
from urllib.parse import urlparse

import requests

QUEUES = [
    ("output/send_sol_notice.csv", "SOL Expungement Notices"),
    ("output/send_irs_complaint.csv", "501(r) Regulatory Complaints"),
    ("output/priority_queue.csv", "Certified Mail Buffer Warnings"),
]

REQUIRED_COLUMNS = {
    "Account ID",
    "Document ID",
    "Violation Type",
    "Action Deadline",
    "Status",
}
MAX_ATTEMPTS = 3


class DispatchError(Exception):
    """Safe-to-log dispatch failure; contains no request or response body."""


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


def validate_endpoint(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise RuntimeError("Dispatch endpoint must be a valid HTTPS URL.")


def load_rows(path: str) -> list[dict[str, str]]:
    if not os.path.isfile(path):
        return []

    with open(path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise RuntimeError(f"{path}: CSV has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise RuntimeError(
                f"{path}: missing columns: {', '.join(sorted(missing))}"
            )

        rows = list(reader)

    for row_number, row in enumerate(rows, start=2):
        for column in REQUIRED_COLUMNS:
            if not (row.get(column) or "").strip():
                raise RuntimeError(
                    f"{path}: blank required value in row {row_number}."
                )

    return rows


def idempotency_key(secret: bytes, category: str, row: dict[str, str]) -> str:
    identity = {
        "category": category,
        "account_id": row["Account ID"].strip(),
        "document_id": row["Document ID"].strip(),
        "violation_type": row["Violation Type"].strip(),
        "action_deadline": row["Action Deadline"].strip(),
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        secret, canonical.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def post_work_order(
    session: requests.Session,
    endpoint: str,
    secret: bytes,
    category: str,
    row: dict[str, str],
) -> None:
    key = idempotency_key(secret, category, row)
    payload = {
        "category": category,
        "account_id": row["Account ID"].strip(),
        "document_id": row["Document ID"].strip(),
        "violation_type": row["Violation Type"].strip(),
        "action_deadline": row["Action Deadline"].strip(),
        "status": row["Status"].strip(),
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.post(
                endpoint,
                json=payload,
                headers={"Idempotency-Key": key},
                timeout=(5, 20),
                allow_redirects=False,
            )
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == MAX_ATTEMPTS:
                raise DispatchError(
                    f"network failure ({type(exc).__name__})"
                ) from None
            time.sleep(2 ** (attempt - 1))
            continue
        except requests.RequestException as exc:
            raise DispatchError(
                f"request failure ({type(exc).__name__})"
            ) from None

        # With redirects disabled, explicitly reject all non-2xx responses.
        if 200 <= response.status_code < 300:
            return

        # Retry rate limits and server errors; fail immediately on other statuses.
        if response.status_code == 429 or response.status_code >= 500:
            if attempt < MAX_ATTEMPTS:
                time.sleep(2 ** (attempt - 1))
                continue

        raise DispatchError(f"HTTP status {response.status_code}")


def main() -> int:
    try:
        endpoint = required_env("DISPATCH_WEBHOOK_URL")
        validate_endpoint(endpoint)
        secret = required_env("IDEMPOTENCY_KEY_SECRET").encode("utf-8")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    sent = 0
    failures = 0

    with requests.Session() as session:
        for path, category in QUEUES:
            try:
                rows = load_rows(path)
            except (OSError, csv.Error, RuntimeError) as exc:
                print(f"Cannot process queue {path}: {exc}", file=sys.stderr)
                failures += 1
                continue

            for row in rows:
                try:
                    post_work_order(session, endpoint, secret, category, row)
                    sent += 1
                except DispatchError as exc:
                    print(
                        f"Dispatch failed for {category}, queue {path}: {exc}",
                        file=sys.stderr,
                    )
                    failures += 1

    print(f"Dispatch finished: {sent} accepted, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
