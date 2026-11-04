# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Current         |
| < 1.0   | ❌ End of Life     |

## Reporting a Vulnerability

If you discover a security vulnerability (e.g., hardcoded credentials, privacy leak, citation tampering), please:

1. **DO NOT** open a public GitHub Issue
2. Report via GitHub Security Advisories: [Connect with Maintainers]
3. Include reproduction steps and potential impact
4. Allow 14 days for response before public disclosure

## Data Privacy

This toolkit **never** collects or transmits:
- Patient names or identifiers
- Account numbers or policy IDs
- Medical treatment details
- Financial information

All data remains on the user's device unless they manually upload it to regulatory agencies.

## Credential Management

Secrets must be managed via environment variables:
```bash
export SMTP_PASSWORD="your-app-password"
python automation/python/nsa_dispute_reminder.py
