#!/usr/bin/env python3
"""Zero-dependency local repository and environment validation runner."""

import os
import stat
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Core paths required for repository validity
REQUIRED_PATHS = [
    Path(".github/workflows/python-ci.yml"),
    Path("scripts/dispatch_work_orders.py"),
    Path("scripts/generate_notices.py"),
    Path("tests/test_cms.py"),
    Path("data/debts.json"),
]

# Files requiring strict restricted permissions (0o600 / rw-------)
RESTRICTED_FILES = [
    Path("data/debts.json"),
]


def log_status(prefix: str, message: str, success: bool = True) -> None:
    symbol = "✓" if success else "✗"
    print(f"[{symbol}] {prefix}: {message}")


def check_repository_structure(root: Path) -> bool:
    print("\n--- 1. Repository Structure Audit ---")
    all_found = True
    for relative_path in REQUIRED_PATHS:
        full_path = root / relative_path
        if full_path.exists():
            log_status("Structure", f"Found required file: {relative_path}")
        else:
            log_status("Structure", f"Missing required file: {relative_path}", success=False)
            all_found = False
    return all_found


def check_file_permissions(root: Path) -> bool:
    print("\n--- 2. File Permission Security Audit ---")
    all_secure = True
    for relative_path in RESTRICTED_FILES:
        full_path = root / relative_path
        if not full_path.exists():
            continue
        
        mode = full_path.stat().st_mode
        file_perm = stat.S_IMODE(mode)
        
        # Check if group or others have any permissions (mask 0o077)
        if file_perm & 0o077 != 0:
            log_status(
                "Security",
                f"Insecure permissions on {relative_path}: octal({oct(file_perm)}) - expected 0o600",
                success=False
            )
            all_secure = False
        else:
            log_status("Security", f"Correct strict permissions on {relative_path}: octal({oct(file_perm)})")
    return all_secure


def check_environment_secrets() -> bool:
    print("\n--- 3. Local Environment Variables Audit ---")
    secret = os.environ.get("HMAC_SECRET", "")
    webhook = os.environ.get("DISPATCH_WEBHOOK_URL", "")
    valid = True

    if not secret:
        log_status("Env", "HMAC_SECRET is missing from local environment (Warning only for local offline runs)", success=False)
    elif len(secret) < 32:
        log_status("Env", f"HMAC_SECRET length ({len(secret)} bytes) is below minimum required 32 bytes", success=False)
        valid = False
    else:
        log_status("Env", "HMAC_SECRET meets 32-byte security requirement")

    if webhook and not webhook.startswith("https://"):
        log_status("Env", "DISPATCH_WEBHOOK_URL must use HTTPS protocol", success=False)
        valid = False
    elif webhook:
        log_status("Env", "DISPATCH_WEBHOOK_URL is valid HTTPS endpoint")
    else:
        log_status("Env", "DISPATCH_WEBHOOK_URL unset (Optional for local test runs)")

    return valid


def run_pytest_suite() -> bool:
    print("\n--- 4. Executing Unit Test Suite ---")
    try:
        cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode == 0:
            log_status("Pytest", "All unit tests passed successfully")
            return True
        else:
            log_status("Pytest", f"Test suite failed with exit code {result.returncode}", success=False)
            return False
    except Exception as e:
        log_status("Pytest", f"Failed to execute pytest runner: {e}", success=False)
        return False


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    print(f"Starting Local Repository Audit on: {repo_root}")

    structure_ok = check_repository_structure(repo_root)
    permissions_ok = check_file_permissions(repo_root)
    env_ok = check_environment_secrets()
    tests_ok = run_pytest_suite()

    print("\n================ Audit Summary ================")
    print(f"Structure Check   : {'PASS' if structure_ok else 'FAIL'}")
    print(f"Permissions Check : {'PASS' if permissions_ok else 'FAIL'}")
    print(f"Environment Check : {'PASS' if env_ok else 'FAIL'}")
    print(f"Unit Test Suite   : {'PASS' if tests_ok else 'FAIL'}")
    print("===============================================")

    if not (structure_ok and permissions_ok and env_ok and tests_ok):
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
