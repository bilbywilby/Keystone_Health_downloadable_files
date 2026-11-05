#!/usr/bin/env python3
"""
pytest unit tests for medical_debt_cms.dispatch_work_orders
Note: These mock external calls; real integration requires a live webhook URL.
"""

import pytest
import json
from unittest.mock import Mock, patch
import datetime as dt
from medical_debt_cms import (
    current_date,
    redact_account_id,
    idempotency_key,
    build_payload,
    post_with_retry,
)

# Sample valid debt record
SAMPLE_DEBT = {
    "account_id": "ACC-1003",
    "document_id": "SOL-TERM-001",
    "violation_type": "Time-barred SOL under 42 Pa.C.S. § 5525(a)",
    "action_deadline": "2026-11-05T00:00:00Z",
    "status": "PENDING_DISPATCH",
    "risk_tier": "RED",
}

@pytest.fixture
def mock_session():
    session = Mock(spec=requests.Session)
    session.post.return_value = Mock(status_code=200, text='{"ok":true}')
    return session

@pytest.mark.parametrize(
    "account_id,expected_tier",
    [
        ("ACC-1003", "RED"),
        ("ACC-1011", "RED"),
        ("ACC-1008", "YELLOW"),
    ],
)
def test_classify_risk(account_id: str, expected_tier: str):
    assert classify_risk({"account_id": account_id, "violation_type": "Upcoming FAP deadline"}) == expected_tier

def test_build_payload(mock_session: Mock):
    item = SAMPLE_DEBT.copy()
    key = idempotency_key(
        item["account_id"],
        item["document_id"],
        item["action_deadline"],
    )
    expected = {
        "account_id": redact_account_id(item["account_id"]),
        "document_id": redact_account_id(item["document_id"]),
        "violation_type": item["violation_type"],
        "action_deadline": item["action_deadline"],
        "status": item["status"],
        "source_timestamp": current_date().isoformat(),
        "idempotency_key": key,
        "risk_tier": item["risk_tier"],
    }
    result = build_payload(item)
    assert result == expected

@patch("requests.Session")
def test_post_with_retry(mock_session: Mock, caplog: pytest.LogCaptureFixture):
    url = "https://test.example.com/dispatch"
    payload = {"foo": "bar"}
    key = "abc123"
    mock_response = Mock(status_code=200)
    mock_session.post.return_value = mock_response

    # First attempt succeeds
    res = post_with_retry(mock_session, url, payload, key, max_retries=1)
    assert res is True
    assert caplog.records[-1].message.startswith("[WARN]")

    # Second attempt fails due to 5xx
    mock_response.status_code = 503
    res = post_with_retry(mock_session, url, payload, key, max_retries=2)
    assert res is False
    assert caplog.records[-1].message.startswith("[ERROR] HTTP 503")

def test_load_debts_no_file():
    with patch.dict(os.environ, {"LEDGER_ENC_KEY": b"real-key"}):
        debts = load_debts("nonexistent.json")
        assert debts == []

def test_redaction_hash_distinctness():
    raw_id = "ACC-1003"
    key = b"shared-secret"
    h1 = hmac.new(key, raw_id.encode(), hashlib.sha256).hexdigest()
    h2 = hmac.new(key, raw_id.encode(), hashlib.sha256).hexdigest()
    assert h1 != h2
