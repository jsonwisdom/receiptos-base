#!/usr/bin/env bash
# validate-spec.sh — Verify required CEG specification files are present.
# Infrastructure only. No protocol semantics.
set -euo pipefail

REQUIRED=(
  "spec/EVIDENCE_GRAPH.md"
  "spec/CONFORMANCE.md"
  "spec/GOVERNANCE.md"
  "spec/RELEASE.md"
)

MISSING=0
for f in "${REQUIRED[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "FAIL: required specification file missing: $f"
    MISSING=1
  else
    echo "OK: $f"
  fi
done

if [[ $MISSING -ne 0 ]]; then
  echo "Specification validation FAILED"
  exit 1
fi

echo "Specification validation PASSED"
exit 0
