#!/usr/bin/env bash
set -euo pipefail

ANCHOR_JSON="${1:-evidence/receipts/eas-global-forest-anchor.json}"

# Expected anchor UID:
# 0xa29eab49ab595b5d93dcb07e612dc0d284c83f2038f5a226c91d7cf9c2b96aa4

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

pass() {
  echo "PASS: $*"
}

[ -n "${BASE_RPC_URL:-}" ] || fail "BASE_RPC_URL required"
command -v jq >/dev/null || fail "jq required"
[ -f "$ANCHOR_JSON" ] || fail "missing anchor receipt: $ANCHOR_JSON"

ANCHOR_UID="$(jq -r '.uid' "$ANCHOR_JSON")"

[ "$ANCHOR_UID" != "null" ] || fail "missing uid in $ANCHOR_JSON"

scripts/verify-eas-anchor-onchain.sh "$ANCHOR_JSON"

pass "EAS attestation remains unrevoked: $ANCHOR_UID"
echo "PASS"
