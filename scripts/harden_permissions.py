#!/usr/bin/env bash
# Strict atomic permission hardening utility for sensitive datasets and configs.

set -euo pipefail

# Define sensitive relative target file paths
TARGET_FILES=(
  "data/debts.json"
  "data/generated_notices.json"
  ".env"
)

# Define sensitive target directory paths
TARGET_DIRS=(
  "data"
)

# Resolve repository root path
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Permission Hardening Operations ==="
echo "Repository Root: ${REPO_ROOT}"

# 1. Enforce 0700 on target directories
for rel_dir in "${TARGET_DIRS[@]}"; do
  full_dir="${REPO_ROOT}/${rel_dir}"
  if [[ -d "${full_dir}" ]]; then
    chmod 700 "${full_dir}"
    echo "[✓] Set 0700 on directory: ${rel_dir}"
  else
    echo "[!] Directory not found (skipping): ${rel_dir}"
  fi
done

# 2. Enforce 0600 on target files
for rel_file in "${TARGET_FILES[@]}"; do
  full_file="${REPO_ROOT}/${rel_file}"
  if [[ -f "${full_file}" ]]; then
    chmod 600 "${full_file}"
    echo "[✓] Set 0600 on file: ${rel_file}"
  else
    echo "[!] File not found (skipping): ${rel_file}"
  fi
done

# 3. Secure any additional sensitive files matching target extensions in data/
if [[ -d "${REPO_ROOT}/data" ]]; then
  find "${REPO_ROOT}/data" -type f \( -name "*.json" -o -name "*.csv" -o -name "*.key" \) -exec chmod 600 {} +
  echo "[✓] Applied 0600 to all data artifacts in data/"
fi

echo "=== Hardening Complete ==="
