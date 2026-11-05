#!/usr/bin/env bash
# ==============================================================================
# verify_deployment.sh — Production Deployment Readiness Verification Suite
# ==============================================================================
set -euo pipefail

# Severity levels
readonly L_SUCCESS=0
readonly L_WARNING=1
readonly L_CRITICAL=2

OVERALL_STATUS=$L_SUCCESS

log_result() {
    local level="$1"
    local name="$2"
    local message="$3"
    
    if [ "$level" -eq $L_CRITICAL ]; then
        echo "❌ [CRITICAL] $name: $message"
        OVERALL_STATUS=$L_CRITICAL
    elif [ "$level" -eq $L_WARNING ]; then
        echo "⚠️  [WARNING]  $name: $message"
        if [ "$OVERALL_STATUS" -lt $L_WARNING ]; then
            OVERALL_STATUS=$L_WARNING
        fi
    else
        echo "✅ [SUCCESS] $name: $message"
    fi
}

echo "=== Starting Deployment Readiness Verification ==="

# ------------------------------------------------------------------------------
# Check 1: Core File Structure Presence
# ------------------------------------------------------------------------------
MISSING_FILES=0
for f in "README.md" "DISCLAIMER.md" "scripts/generate_notices.py" "scripts/dispatch_work_orders.py" "tests/test_cms.py"; do
    if [ ! -f "$f" ]; then
        echo "Missing required file: $f"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ "$MISSING_FILES" -eq 0 ]; then
    log_result $L_SUCCESS "File Structure" "All mandatory repository files present."
else
    log_result $L_CRITICAL "File Structure" "Missing $MISSING_FILES mandatory file(s)."
fi

# ------------------------------------------------------------------------------
# Check 2: Statutory Citation Reference Verification
# ------------------------------------------------------------------------------
if grep -rn "PHSA § 2799" templates/ data/ README.md 2>/dev/null || grep -rn "42 U.S.C. § 300gg-111" templates/ data/ README.md 2>/dev/null; then
    log_result $L_SUCCESS "Statutory References" "Required federal statutory anchors detected."
else
    log_result $L_WARNING "Statutory References" "Standard statutory citation strings not found in template files."
fi

# ------------------------------------------------------------------------------
# Check 3: Python Unit Tests Execution via Pytest
# ------------------------------------------------------------------------------
if command -v pytest &>/dev/null; then
    if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
        if pytest -q tests/; then
            log_result $L_SUCCESS "Unit Tests" "All pytest suites executed and passed successfully."
        else
            log_result $L_CRITICAL "Unit Tests" "Pytest suite execution encountered test failures."
        fi
    else
        log_result $L_CRITICAL "Unit Tests" "Test directory missing or empty."
    fi
else
    log_result $L_CRITICAL "Unit Tests" "pytest command not found in environment."
fi

# ------------------------------------------------------------------------------
# Check 4: Secret Scanning in automation/python/ & scripts/
# ------------------------------------------------------------------------------
SECRET_MATCHES=0
for target_dir in "automation/python" "scripts"; do
    if [ -d "$target_dir" ]; then
        if grep -rnE "(sk_live_|api_key|password\s*=\s*['\"])" "$target_dir" 2>/dev/null; then
            SECRET_MATCHES=$((SECRET_MATCHES + 1))
        fi
    fi
done

if [ "$SECRET_MATCHES" -eq 0 ]; then
    log_result $L_SUCCESS "Secret Scan" "No hardcoded high-risk secret patterns detected."
else
    log_result $L_CRITICAL "Secret Scan" "Potential hardcoded secrets detected in source paths."
fi

# ------------------------------------------------------------------------------
# Final Verdict
# ------------------------------------------------------------------------------
echo "=================================================="
if [ "$OVERALL_STATUS" -eq $L_CRITICAL ]; then
    echo "VERDICT: DEPLOYMENT BLOCKED (Critical errors found)"
    exit 2
elif [ "$OVERALL_STATUS" -eq $L_WARNING ]; then
    echo "VERDICT: DEPLOYMENT RESTRICTED (Warnings require review)"
    exit 1
else
    echo "VERDICT: DEPLOYMENT READY"
    exit 0
fi
