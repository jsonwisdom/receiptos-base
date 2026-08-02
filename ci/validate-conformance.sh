#!/usr/bin/env bash
# validate-conformance.sh — Verify conformance bundle layout exists.
# Does not require frozen artifacts; only checks structure.
# Infrastructure only. No protocol semantics.
set -euo pipefail

BASE="conformance/v1.0"
REQUIRED_DIRS=(
  "ledger"
  "canonicalization"
  "provenance"
  "graph_integrity"
  "promotion"
  "replay"
  "final"
)

if [[ ! -d "$BASE" ]]; then
  echo "FAIL: conformance/v1.0 directory missing"
  exit 1
fi

MISSING=0
for d in "${REQUIRED_DIRS[@]}"; do
  if [[ ! -d "$BASE/$d" ]]; then
    echo "FAIL: required directory missing: $BASE/$d"
    MISSING=1
  else
    echo "OK: $BASE/$d"
  fi
done

if [[ -f "$BASE/README.md" ]]; then
  echo "OK: $BASE/README.md"
else
  echo "WARN: $BASE/README.md not present (recommended)"
fi

if [[ $MISSING -ne 0 ]]; then
  echo "Conformance layout validation FAILED"
  exit 1
fi

echo "Conformance layout validation PASSED"
exit 0
