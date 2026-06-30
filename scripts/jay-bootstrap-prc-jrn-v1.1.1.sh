#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/jsonwisdom/receiptos-base.git"
REPO_DIR="${1:-receiptos-base}"

printf '== PRC-JRN v1.1.1 bootstrap ==\n'

if [ ! -d "$REPO_DIR/.git" ]; then
  if [ -e "$REPO_DIR" ]; then
    echo "ERROR: $REPO_DIR exists but is not a git repo. Move it or pass a different target dir." >&2
    exit 1
  fi
  git clone "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"
git fetch origin main --tags
git checkout main
git pull --ff-only origin main

mkdir -p curriculum modules/prc-jrn receipts/prc-jrn/ext/raw audits/PRC-JRN-v1.1

required_paths=(
  "curriculum/prc-jrn-v1.1.md"
  "curriculum/prc-jrn-v1.1.1-patch.md"
  "modules/prc-jrn/engine.js"
  "modules/prc-jrn/receipt.schema.json"
  "modules/prc-jrn/validation-index.json"
  "receipts/prc-jrn/ext/EXT-001-intake-template.json"
  "receipts/prc-jrn/ext/PRC-JRN-FIELD-EXT-002.json"
  "receipts/prc-jrn/ext/PRC-JRN-FIELD-EXT-003.json"
  "receipts/prc-jrn/ext/PRC-JRN-FIELD-EXT-004.json"
  "receipts/prc-jrn/ext/PRC-JRN-FIELD-EXT-005.json"
)

missing=0
for path in "${required_paths[@]}"; do
  if [ ! -f "$path" ]; then
    echo "MISSING: $path"
    missing=1
  else
    echo "OK: $path"
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "Bootstrap incomplete: required paths missing after pull." >&2
  exit 1
fi

if command -v node >/dev/null 2>&1; then
  echo
  echo "== Engine smoke =="
  node modules/prc-jrn/engine.js
else
  echo "WARN: node not found; skipped engine smoke."
fi

if command -v jq >/dev/null 2>&1; then
  echo
  echo "== Validation index =="
  jq '{framework_version,status,authority,authentic_external_receipts,synthetic_validation_receipts,external_receipt_queue}' modules/prc-jrn/validation-index.json
fi

echo
echo "== Git state =="
git rev-parse HEAD
git status --short

echo
echo "PRC-JRN v1.1.1 local bootstrap complete. EXT-001 remains intake-only pending authentic participant payload."
