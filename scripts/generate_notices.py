#!/usr/bin/env python3
"""
Generate legally grounded enforcement documents from debt records.
Usage: python generate_notices.py data/debts.json > output/notices.txt
"""

import json
import os
from pathlib import Path

OUTPUT_DIR = Path("output/notices")
OUTPUT_DIR.mkdir(exist_ok=True)

def get_formatted_date(date_str: str) -> str:
    """Normalize date string for notices."""
    try:
        dt = datetime.datetime.fromisoformat(date_str)
        return dt.strftime("%B %d, %Y")
    except Exception:
        return "[DATE]"

def generate_pa_sol_notice(record: dict) -> str:
    """
    Generates a formal demand under 42 Pa.C.S. § 5525(a) asserting time-barred status.
    """
    sol_expiration = record.get("sol_expiration_date", "[EXPIRATION_DATE]")
    last_payment = record.get("last_payment_date", "[LAST_PAYMENT_DATE]")

    notice = f"""LEGAL NOTICE: DEMAND TO CEASE COLLECTION ACTIVITY
Date: {datetime.date.today().strftime('%m/%d/%Y')}
Via Certified Mail (Return Receipt Requested)

TO:
{record['collector_name']}
{record['collector_address']}

RE: Account Number: REDACTED ({record['account_id']})
Original Creditor: {record['original_creditor']}
Stated Balance: ${record['amount']:.2f}
Last Voluntary Payment / Default: {get_formatted_date(last_payment)}

To Whom It May Concern,

This letter serves as formal notification that the alleged debt referenced above is time-barred under the applicable Pennsylvania Statute of Limitations, 42 Pa.C.S. § 5525(a), which establishes a strict four-year limitation period for actions upon a contract, obligation, or liability founded upon a writing.

According to your records and verified transaction history, the cause of action accrued on {get_formatted_date(record['last_payment_date'])}. The statutory four-year period expired on {get_formatted_date(sol_expiration)}.

Legal Demands & Statutory Mandates:
1. CEASE AND DESIST: Pursuant to 15 U.S.C. § 1692c(c) (FDCPA) and the Pennsylvania Fair Credit Extension Uniformity Act (73 P.S. § 2270.4), you are hereby directed to cease all further communication regarding this debt, including telephonic calls, written demands, and electronic contacts.
2. NO PAYMENT REVIVAL ACKNOWLEDGMENT: Be advised that no payment, promise of payment, or acknowledgment of this debt will be made. Under Pennsylvania law, unwritten promises do not toll or revive the statutory period after expiration.
3. CREDIT REPORTING WARNING: Threatening or pursuing legal action, or placing/maintaining an inaccurate trade line on a credit report for a time-barred debt without clear disclosure of its unenforceable status, constitutes a deceptive trade practice under 73 P.S. § 201-1 et seq. (UTPCPL) and 15 U.S.C. § 1692e.

If you contend that the statute of limitations has not expired, provide written verification within thirty (30) days detailing the specific legal basis and documented tolling events. Absent such proof, confirm in writing that this account is permanently closed and returned to zero balance.

Sincerely,

Authorized Representative / Consumer
Account Ref ID: {record['account_id']}
Timestamp: {datetime.datetime.now().isoformat()}
"""

def generate_irs_501r_complaint(record: dict) -> str:
    """
    Generates a regulatory complaint package under IRC § 501(r)(4)-(6) for submission alongside IRS Form 13909.
    """
    hospital_ein = record.get('hospital_ein', 'EXEMPT-HOSPITAL')
    facility_name = record.get('hospital_name', '[HOSPITAL_NAME]')
    service_date = record.get('date_of_service', '[SERVICE_DATE]')

    complaint = f"""REGULATORY COMPLAINT: VIOLATION OF IRC § 501(r) FINANCIAL ASSISTANCE & ECA RULES
Submission Type: IRS Form 13909 Attachment / PA Office of Attorney General Complaint
Target Facility: {facility_name} (EIN: {hospital_ein})
Facility Address: {record['hospital_address']}

COMPLAINANT / PATIENT REF: {record['account_id']}
DATE OF SERVICE: {service_date}
DISPATCH DEADLINE: {record['action_deadline']}

I. STATEMENT OF FACTS
1. {facility_name} is organized as a tax-exempt charitable hospital organization operating under Internal Revenue Code Section 501(c)(3).
2. Pursuant to IRC § 501(r)(4) and Treas. Reg. § 1.501(r)-4, the facility is required to maintain a written Financial Assistance Policy (FAP) and widely publicize it throughout the community.
3. Pursuant to IRC § 501(r)(6) and Treas. Reg. § 1.501(r)-6, the facility is prohibited from engaging in Extraordinary Collection Actions (ECAs)—including legal action, credit bureau reporting, and debt sales—prior to making reasonable efforts to determine whether the individual is FAP-eligible during the mandatory 240-day application window.

II. SPECIFIC STATUTORY VIOLATIONS
[ ] Failure to provide FAP plain language summary prior to initiating collection actions (Treas. Reg. § 1.501(r)-4(b)(5))
[ ] Premature initiation of Extraordinary Collection Actions (ECAs) prior to the expiration of the 120-day notification period (Treas. Reg. § 1.501(r)-6(b))
[ ] Failure to process completed Financial Assistance Application submitted within the 240-day application period (Treas. Reg. § 1.501(r)-6(c))
[ ] Breach of Pennsylvania Medical Care Availability and Reduction of Error (MCARE) and billing fairness standards.

III. EVIDENCE AND TIMELINE SUMMARY
Service Date: {service_date}
Initial Billing Date: {record.get('initial_bill_date', '[INITIAL_BILL_DATE]')}
ECA Initiation Date: {record.get('eca_initiation_date', '[ECA_INIT_DATE]')} (Initiated {record.get('days_elapsed', 'N/A')} days post-billing, violating the 120-day minimum rule.)

IV. REQUESTED REGULATORY ACTION
1. IRS Exempt Organizations Division: Initiate an audit of {facility_name}'s Form 990 Schedule H compliance to assess penalties under IRC § 4959 or revocation of 501(c)(3) tax-exempt status.
2. PA Office of Attorney General (Health Care Section): Investigate deceptive collection practices under the Unfair Trade Practices and Consumer Protection Law (73 P.S. § 201-1 et seq.).
3. Direct the hospital to immediately recall the account from third-party collection agencies and suspend all active ECAs pending full FAP evaluation.

Respectfully submitted,

Enforcement Tracking Key: {record['account_id']}
Timestamp: {datetime.datetime.now().isoformat()}
"""

def process_records(input_path: str = "data/debts.json") -> None:
    """Load debt records and write notices to output directory."""
    p_in = Path(input_path)
    if not p_in.exists():
        print(f"[ERROR] Input file {input_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(p_in, "r", encoding="utf-8") as f:
        records = json.load(f)

    for item in records:
        acc_id = item.get("account_id", "UNKNOWN").replace("/", "_")
        v_type = item.get("violation_type", "")

        out_file = OUTPUT_DIR / f"{acc_id}_{v_type.replace('/', '_').replace(' ', '_').lower()}.txt"
        content = ""
        if "SOL" in v_type or "Time-barred" in v_type:
            content = generate_pa_sol_notice(item)
        elif "501(r)" in v_type or "FAP" in v_type or "ECA" in v_type:
            content = generate_irs_501r_complaint(item)
        else:
            continue

        with open(out_file, "w", encoding="utf-8") as out:
            out.write(content)
        print(f"✅ Generated: {out_file}")

if __name__ == "__main__":
    process_records()
