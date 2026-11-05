## 1. Executive Summary
The goal of this project is to provide Pennsylvania residents with a structured, legally-grounded system to fight unlawful medical bills. The system moves the consumer from a state of distress to a state of structured advocacy by utilizing a "Triage $\rightarrow$ Freeze $\rightarrow$ Dispute $\rightarrow$ Escalate" workflow.

The project is designed to bridge the gap between complex federal/state statutes and the lived experience of a consumer who cannot afford legal counsel.

---

## 2. The "Triad" of Deliverables
The project consists of three primary interlocking components:

### A. The Master Framework (README Rev 4.1)
*   **Purpose:** Technical reference and legal source-of-truth.
*   **Core Logic:** Maps specific medical billing scenarios to statutory protections.
*   **Key Citations:**
    *   **Federal:** No Surprises Act (45 C.F.R. Part 149), IRS § 501(r) (Non-profit charity care).
    *   **PA State:** Act 146 of 2022 (External Review), FCEUA (Debt Collection), UTPCPL (Consumer Protection), and 42 Pa.C.S. § 5525/5533 (Statute of Limitations).

### B. The Consumer Plaintext Guide
*   **Purpose:** User interface for the distressed consumer.
*   **Architecture:** 
    *   **Triage Quiz:** Routes users to "Type A" (NSA), "Type B" (FAP), or "Type C" (Standard) disputes.
    *   **Risk Framing:** High-visibility "Red Zone" warnings regarding court papers and "micro-payments."
    *   **Timeline:** Segmented into Day 0–7 (Preserve), Day 7–30 (Dispute), and Day 30–60 (Escalate).

### C. The Dispute Tracker Spreadsheet
*   **Purpose:** Case management and deadline automation.
*   **Automation Logic:**
    *   **ECA Deadline:** $\text{First Bill Date} + 120\text{ days}$ (Non-profit).
    *   **FAP Deadline:** $\text{First Bill Date} + 240\text{ days}$ (Non-profit).
    *   **SOL Expiration:** $\text{Service Date} + 4\text{ years}$ (PA Written Contract).

---

## 3. Critical Technical/Legal Nuances
The following points are high-risk and must be maintained by any future iterations:

1.  **The "Micro-Payment" Trap:** In PA, paying even a small amount toward an old debt can potentially restart the 4-year Statute of Limitations clock. The guide strictly forbids this.
2.  **The Pincer Movement:** The strategy emphasizes filing a regulatory complaint (CMS/PID) *simultaneously* with a final demand letter to the provider to maximize the probability of an administrative hold.
3.  **Plan Distinction:** The system distinguishes between **Fully Insured** (State regulated $\rightarrow$ PID) and **Self-Funded/ERISA** (Federally regulated $\rightarrow$ CMS). This is the single most common failure point in consumer disputes.
4.  **Court Priority:** Regulator complaints do **not** stay court proceedings. The framework prioritizes immediate legal counsel over regulatory filing if a summons has been received.

---

## 4. Pending Verification Flags `[VERIFY]`
The following items are noted as "conflict-prone" or "subject to change" and require primary source validation before final publication:

*   **CMS Help Desk Number:** Conflict exists between `1-800-985-3059` (dedicated NSA line) and `1-800-MEDICARE`. The framework currently favors the dedicated line.
*   **QPA Methodology:** The Qualifying Payment Amount (QPA) calculation has been subject to ongoing litigation; verify the most current benchmark rules.
*   **Air Ambulance:** Verify 45 C.F.R. § 149.230 for any 2026 updates regarding non-emergency transportation.
*   **IDR Gateway:** Confirm current administrative fees and portal requirements for the 2026 CMS IDR process.

---

## 5. Next Steps for the Successor
1.  **Final Primary Source Audit:** Run the `[VERIFY]` list against `cms.gov` and `pid.pa.gov`.
2.  **Template Finalization:** Ensure all six core letters are formatted as clean, editable documents (Markdown or .docx).
3.  **Spreadsheet Build:** Convert the provided logic specifications into a functional Excel/Google Sheets file with the defined conditional formatting.
4.  **Deployment:** Package as a GitHub repository or a downloadable PDF toolkit.
