```markdown
# Test Suite

This document describes the automated tests for the Keystone Health No Surprises Act Dispute Toolkit.

## Run the tests

From the repository root:

```bash
python -m pytest tests/ -v
```

To run an individual module:

```bash
python -m pytest tests/test_citation_accuracy.py -v
python -m pytest tests/test_csv_validity.py -v
python -m pytest tests/test_script_functionality.py -v
```

The suite requires `pytest`; the CSV tests also require `pandas`. Install dependencies using the repository’s development-dependency instructions, if available.

## Test modules

### `tests/test_citation_accuracy.py`

Checks selected citation strings and template formatting in configured Markdown and plain-text files.

These checks compare text against configured rules. They do **not** establish that a citation is current, applies to a particular dispute, or supports a legal claim. Review citation allowlists and exclusions against primary legal sources and with qualified counsel. Ensure test fixtures and documentation do not unintentionally trigger banned-string checks.

### `tests/test_csv_validity.py`

Checks the dispute tracker’s expected columns, parses the CSV, checks required fields, and attempts to parse date fields.

The current all-CSV check only verifies that `pandas` can read a file. Its `len(df) >= 0` assertion does not validate row structure. Add explicit per-file schemas or row-width checks if other CSV files require stronger validation.

### `tests/test_script_functionality.py`

Is intended to cover reminder-script environment configuration, state persistence, duplicate-notification suppression, and date-handling edge cases.

Tests should call the reminder script’s actual functions or command-line entry point. Writing and reading a sample state file inside a test does not verify that the script itself persists state or suppresses duplicate emails. Use temporary state files and mock the mail-sending interface so tests cannot send real messages.

## Known limitations before release

- A missing critical template should fail the test, not be skipped. Use skips only for explicitly optional files.
- Citation-format checks should use an exact, reviewed set of allowed sections. A numeric-range check alone does not verify that a CFR section exists.
- Clearly distinguish tests that check for required citations from reviews of legal accuracy.
- Date tests should enforce the project’s chosen date format rather than rely on a permissive parser.
- Do not commit real SMTP credentials. Use dummy values and mocks in tests.
- The test-generation script writes to test files in overwrite mode. Review its output before running it on files that may contain manual changes.

## CI and release checklist

- [ ] Run the full test suite from the repository root.
- [ ] Record the actual test result; do not describe generated tests as passing until they have been run.
- [ ] Run tests in CI for pull requests that change templates, documentation, tracker files, or reminder automation.
- [ ] Ensure reminder tests use isolated temporary files and mocked email delivery.
- [ ] Review citation rules separately against primary sources. Passing tests do not constitute legal review.
```
