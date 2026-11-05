import datetime
import pytest
from dateutil.relativedelta import relativedelta

# System date fixed to November 5, 2026
CURRENT_DATE = datetime.date(2026, 11, 5)

# Test dataset matching the 15 managed accounts
ACCOUNTS = [
    {"id": "ACC-1001", "type": "Non-Profit", "first_statement": datetime.date(2026, 2, 1), "dvr_delivered": datetime.date(2026, 3, 8)},
    {"id": "ACC-1002", "type": "For-Profit", "first_statement": datetime.date(2025, 11, 15), "dvr_delivered": None},
    {"id": "ACC-1003", "type": "For-Profit", "first_statement": datetime.date(2022, 6, 10), "dvr_delivered": datetime.date(2022, 8, 5)},
    {"id": "ACC-1004", "type": "Non-Profit", "first_statement": datetime.date(2026, 7, 15), "dvr_delivered": None},
    {"id": "ACC-1005", "type": "For-Profit", "first_statement": datetime.date(2026, 10, 10), "dvr_delivered": datetime.date(2026, 10, 18)},
    {"id": "ACC-1006", "type": "Non-Profit", "first_statement": datetime.date(2022, 2, 1), "dvr_delivered": None},
    {"id": "ACC-1007", "type": "For-Profit", "first_statement": datetime.date(2023, 4, 1), "dvr_delivered": None},
    {"id": "ACC-1008", "type": "Non-Profit", "first_statement": datetime.date(2026, 5, 1), "dvr_delivered": datetime.date(2026, 5, 14)},
    {"id": "ACC-1009", "type": "For-Profit", "first_statement": datetime.date(2021, 12, 15), "dvr_delivered": None},
    {"id": "ACC-1010", "type": "Non-Profit", "first_statement": datetime.date(2026, 10, 20), "dvr_delivered": datetime.date(2026, 10, 25)},
    {"id": "ACC-1011", "type": "Non-Profit", "first_statement": datetime.date(2025, 8, 25), "dvr_delivered": None},
    {"id": "ACC-1012", "type": "For-Profit", "first_statement": datetime.date(2026, 9, 1), "dvr_delivered": datetime.date(2026, 9, 14)},
    {"id": "ACC-1013", "type": "For-Profit", "first_statement": datetime.date(2026, 9, 15), "dvr_delivered": datetime.date(2026, 10, 4)},
    {"id": "ACC-1014", "type": "For-Profit", "first_stage": datetime.date(2026, 3, 1), "first_statement": datetime.date(2026, 3, 1), "dvr_delivered": datetime.date(2026, 3, 14)},
    {"id": "ACC-1015", "type": "Non-Profit", "first_statement": datetime.date(2020, 6, 1), "dvr_delivered": None},
]

def calculate_sol(first_statement):
    # 4 years from first statement date (EDATE equivalent)
    return first_statement + relativedelta(years=4)

@pytest.mark.parametrize("acc_id,expected_barred", [
    ("ACC-1001", False),
    ("ACC-1003", True),   # Expired June 10, 2026
    ("ACC-1006", True),   # Expired Feb 1, 2026
    ("ACC-1009", True),   # Expired Dec 15, 2025
    ("ACC-1015", True),   # Expired June 1, 2024
])
def test_statute_of_limitations(acc_id, expected_barred):
    account = next(a for a in ACCOUNTS if a["id"] == acc_id)
    sol_date = calculate_sol(account["first_statement"])
    is_barred = CURRENT_DATE > sol_date
    assert is_barred == expected_barred, f"Account {acc_id} SOL status mismatch."

@pytest.mark.parametrize("acc_id,expected_violation", [
    ("ACC-1011", True),   # FAP 240-day window expired April 2026
    ("ACC-1001", False),  # Within active window
])
def test_fap_501r_compliance(acc_id, expected_violation):
    account = next(a for a in ACCOUNTS if a["id"] == acc_id)
    if account["type"] == "Non-Profit":
        fap_deadline = account["first_statement"] + relativedelta(days=240)
        violation = CURRENT_DATE > fap_deadline
        assert violation == expected_violation, f"Account {acc_id} 501(r) violation status mismatch."
