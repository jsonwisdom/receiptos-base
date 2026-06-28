#!/usr/bin/env bash
set -euo pipefail

ANCHOR_JSON="${1:-evidence/receipts/eas-global-forest-anchor.json}"
CANONICAL_RECEIPT="evidence/receipts/global-forest-verification.json"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

pass() {
  echo "PASS: $*"
}

command -v jq >/dev/null || fail "jq required"
command -v sha256sum >/dev/null || fail "sha256sum required"

[ -f "$ANCHOR_JSON" ] || fail "missing anchor receipt: $ANCHOR_JSON"
[ -f "$CANONICAL_RECEIPT" ] || fail "missing canonical receipt: $CANONICAL_RECEIPT"

LOCAL_RECEIPT_HASH="$(jq -r '.receipt_hash' "$ANCHOR_JSON")"
COMPUTED_HASH="0x$(sha256sum "$CANONICAL_RECEIPT" | awk '{print $1}')"

[ "$LOCAL_RECEIPT_HASH" = "$COMPUTED_HASH" ] || fail "receipt_hash mismatch: local=$LOCAL_RECEIPT_HASH computed=$COMPUTED_HASH"

pass "local receipt_hash matches canonical receipt"
echo "PASS"
