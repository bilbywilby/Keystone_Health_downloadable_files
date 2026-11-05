## 1. Primary Source & Citation Policy

Every substantive claim, statutory reference, regulatory deadline, or phone number added or modified in this repository **must be backed by primary-source verification**.

### Mandatory Source Tiers
When submitting updates to `citations.md` or any document in `guides/`, `templates/`, or `tools/`, classify your source into one of the following tiers:

- **Tier A (Primary Retrieved Standard):** Official government statutes, federal register rules, eCFR updates, binding court decisions (e.g., *45 C.F.R. Part 149*, *PHSA §§ 2799A-1 through 2799A-3*, *26 U.S.C. § 501(r)*, *Act 146 of 2022*).
- **Tier B (Official Agency Catalog / State Statute):** Official guidance bulletins, statutory codes, or verified agency portals (e.g., *Pennsylvania Insurance Department (PID)*, *PA Attorney General*, *Consumer Financial Protection Bureau (CFPB)*, *73 P.S. § 2270.1 et seq.*).
- **Tier C (Unresolved / Under Verification):** Secondary reporting, unverified phone numbers, or disputed legal doctrines (e.g., *42 Pa.C.S. § 5533 reset doctrine*, *CMS IDR portal fee schedules pending official publication*).

### Submitting Citation Changes
1. **Never introduce unverified numbers or figures.** If an agency phone number or fee amount cannot be verified via an official `.gov` site, mark it explicitly with `[VERIFY]` and assign it to Tier C.
2. **Include Exact Pin Cites:** Provide section, subsection, and paragraph numbers (e.g., `45 C.F.R. § 149.420(c)` or `73 P.S. § 2270.4(a)`).
3. **Update `citations.md` and `sources-by-document.md`:** Any pull request adding or altering a legal reference must update both mapping files to keep the audit trail intact.

---

## 2. Directory Structure & File Conventions

All file modifications must respect the repository layout:


keystone-health-defense/
├── README.md                              # Core framework & legal reference
├── LICENSE                                # CC BY-SA 4.0
├── CONTRIBUTING.md                        # This file
├── citations.md                           # Master citation registry
├── sources-by-document.md                 # Per-document citation mapping
│
├── guides/                                # Consumer-facing documentation
│   ├── consumer-guide.md                  # Plaintext "Start Here" triage
│   └── glossary.md                        # Statutory/medical term decoder
│
├── templates/                             # Core letter templates (Plaintext .txt)
│   ├── 01-dispute-letter.txt              # Template #8 (Initial Dispute)
│   ├── 02-fap-demand.txt                  # Template #9 (501(r) FAP Demand)
│   ├── 03-pid-complaint.txt               # Template #10 (PID Complaint)
│   ├── 04-cms-complaint.txt               # Template #11 (CMS NSA Complaint)
│   ├── 05-provider-escalation.txt         # Template #12 (Final Hold Demand)
│   ├── 06-act146-review-request.txt       # Template #13 (Act 146 External Review)
│   └── 07-formal-validation.txt           # Template #8A (Formal Validation Notice)
│
├── tools/                                 # Data tracking utilities
│   ├── Medical_Debt_Tracker.csv           # Tracker v1.1 CSV
│   ├── Medical_Debt_Tracker.xlsx          # Tracker v1.1 Formatted Excel
│   └── tracker-setup.md                   # Formula rules & caveats
│
├── docs/                                  # Audits & regulatory summaries
│   └── source-audit-2026-11.md            # Primary-source audit findings
│
└── outreach/                              # Public outreach & printable materials
├── reddit-post-draft.md               # Community post draft
└── one-page-checklist.pdf             # Printable waiting-room handout

---

## 3. Pull Request Guidelines

Before submitting a Pull Request (PR):

1. **Verify Mathematical & Formula Integrity:**
   - Tracker formulas must execute cleanly in both open-source CSV parsers and Microsoft Excel.
   - Do **not** hardcode calculated legal prompt dates. Use dynamic formulas relative to base fields (e.g., `=IF(E2="","",E2+120)`).
   - Ensure headers clearly distinguish between **Prompts/Reference Dates** and **Statutory Deadlines** to prevent misinterpreting prompts as legal suit deadlines.

2. **Maintain Tone & Objective Framing:**
   - Avoid evaluative or emotional language (e.g., do not label billing practices "good" or "bad").
   - Frame all arguments around objective statutory criteria, compliance metrics, and verified procedural protections.

3. **Check for PII Compliance:**
   - **Never commit real personal health information (PHI) or personally identifiable information (PII).** Use anonymized sample placeholders (e.g., `ACC-1001`, `Sample Non-Profit Hospital`).

4. **Run Validation Checklist:**
   - [ ] All new legal citations are logged in `citations.md`.
   - [ ] Open verification flags are documented in `sources-by-document.md`.
   - [ ] Plaintext templates maintain copy-paste readiness.
   - [ ] No regression in existing test configurations or formulas.

---

## 4. Licensing & Attribution

By submitting a contribution to this repository, you agree that your contributions will be licensed under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** license.

- You retain copyright to your original contributions.
- All derivative works must provide appropriate attribution to the Keystone Health Defense project and maintain open availability under the same CC BY-SA 4.0 license.

2. Outreach Handout Template (outreach/one-page-checklist.txt)
================================================================================
          KEYSTONE HEALTH MEDICAL DEBT DEFENSE: WAITING-ROOM CHECKLIST
================================================================================
           Know Your Rights Under Federal & Pennsylvania Law (2026)
--------------------------------------------------------------------------------

1. STOP BEFORE YOU PAY OR SIGN
   [ ] NEVER pay an out-of-network balance bill on the spot for emergency care,
       air ambulance services, or unexpected out-of-network facility care.
   [ ] DO NOT sign a consent waiver at the hospital unless you were given clear,
       written notice at least 72 hours in advance (45 C.F.R. § 149.420).
   [ ] Air Ambulance Note: Providers CANNOT ask you to waive No Surprises Act
       (NSA) protections for air ambulance transport under any circumstances.

2. GATHER YOUR DOCUMENTS
   [ ] Itemized Bill: Request a full bill showing CPT/HCPCS procedure codes and
       individual line items (not just summary charges).
   [ ] Explanation of Benefits (EOB): Obtain the formal statement from your
       health plan showing "Patient Responsibility."
   [ ] Certified Mail Receipts: Save all mail tracking numbers when sending
       dispute letters to hospitals or collection agencies.

3. IDENTIFY YOUR DISPUTE TYPE & ACTION PATHWAY
   -----------------------------------------------------------------------------
   DISPUTE TYPE          TRIGGERING EVENT                ACTION STEP
   -----------------------------------------------------------------------------
   Type A: NSA           Out-of-network emergency /      Send Dispute Letter
   Balance Bill          ancillary bill received         (Template #8)
   -----------------------------------------------------------------------------
   Type B: Non-Profit    Care at a 501(c)(3) hospital;   Send FAP Demand Letter
   Hospital Bill         FAP assistance needed           (Template #9)
   -----------------------------------------------------------------------------
   Type C: Standard      In-network billing dispute or   Audit itemized bill &
   Billing Dispute       unreasonable pricing charge     negotiate pricing
   -----------------------------------------------------------------------------

4. ENFORCE YOUR RIGHTS & FILE COMPLAINTS
   If the provider or collector refuses to correct the bill after receiving your
   letter, escalate immediately to state and federal regulators:

   [ ] Fully Insured Plans (PA): File an external review with the Pennsylvania
       Insurance Department (PID) under Act 146 of 2022.
       -> Call PID: 1-877-881-6388 | Web: insurance.pa.gov

   [ ] Self-Funded Plans (ERISA) / Federal Protections: File a No Surprises
       Act complaint with CMS.
       -> Web: cms.gov/nosurprises

   [ ] Deceptive Debt Collection Practices: File a complaint under the PA Fair
       Credit Extension Uniformity Act (FCEUA) with the PA Attorney General.
       -> Call PA AG: 1-877-888-4877 | Web: attorneygeneral.gov

5. TRACK YOUR DEADLINES
   [ ] Log your dates using the Keystone Medical Debt Tracker.
   [ ] 120 Days: IRS 501(r) Extra-Ordinary Collection Action (ECA) prompt.
   [ ] 240 Days: IRS 501(r) Financial Assistance Application (FAP) prompt.
   [ ] 4 Years: PA Breach of Contract SOL reference period (42 Pa.C.S. § 5525(a)).

--------------------------------------------------------------------------------
DISCLAIMER: This document is for informational and educational purposes only and
does not constitute formal legal advice. For individual legal counsel, contact a
qualified attorney or your local Pennsylvania Legal Aid Office (palegalfund.org).
================================================================================

