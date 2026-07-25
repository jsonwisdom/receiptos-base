#!/usr/bin/env bash
# ci/scripts/run_fixtures.sh
# Constitutional conformance harness — orchestration only.
# No protocol logic. No schema interpretation. No fixture mutation.
# Exit status is the sole constitutional signal.

set -euo pipefail

# ---------------------------------------------------------------------------
# Parameterized validator locations (required)
# ---------------------------------------------------------------------------
: "${REF_VALIDATOR:?REF_VALIDATOR environment variable must be set}"
: "${CAND_VALIDATOR:?CAND_VALIDATOR environment variable must be set}"

# ---------------------------------------------------------------------------
# Fixture corpus root (fixed relative to repository root)
# ---------------------------------------------------------------------------
FIXTURES_DIR="${FIXTURES_DIR:-fixtures}"

if [[ ! -d "${FIXTURES_DIR}" ]]; then
  echo "ERROR: fixture corpus directory not found: ${FIXTURES_DIR}" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Execute reference validator
# ---------------------------------------------------------------------------
echo "==> Running reference validator: ${REF_VALIDATOR}"
# shellcheck disable=SC2086
${REF_VALIDATOR} "${FIXTURES_DIR}"
REF_EXIT=$?

if [[ ${REF_EXIT} -ne 0 ]]; then
  echo "ERROR: reference validator exited ${REF_EXIT}" >&2
  exit ${REF_EXIT}
fi

# ---------------------------------------------------------------------------
# Execute candidate validator
# ---------------------------------------------------------------------------
echo "==> Running candidate validator: ${CAND_VALIDATOR}"
# shellcheck disable=SC2086
${CAND_VALIDATOR} "${FIXTURES_DIR}"
CAND_EXIT=$?

if [[ ${CAND_EXIT} -ne 0 ]]; then
  echo "ERROR: candidate validator exited ${CAND_EXIT}" >&2
  exit ${CAND_EXIT}
fi

# ---------------------------------------------------------------------------
# Structural comparison (delegated — no protocol logic here)
# ---------------------------------------------------------------------------
if [[ -x "ci/scripts/compare_reports.py" ]]; then
  echo "==> Running structural comparison"
  python3 ci/scripts/compare_reports.py
  COMPARE_EXIT=$?
  exit ${COMPARE_EXIT}
elif [[ -f "ci/scripts/compare_reports.py" ]]; then
  echo "==> Running structural comparison"
  python3 ci/scripts/compare_reports.py
  COMPARE_EXIT=$?
  exit ${COMPARE_EXIT}
else
  echo "NOTE: compare_reports.py not present — validators executed, comparison skipped"
  exit 0
fi
