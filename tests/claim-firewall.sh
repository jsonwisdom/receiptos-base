#!/bin/bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:3000}"

echo "🧪 Docket #60 — Claim Firewall Stress Test"
echo "─────────────────────────────────────────────"

post_claim() {
  curl -s -X POST "$BASE_URL/api/claims" \
    -H "Content-Type: application/json" \
    -d "$1"
}

expect_contains() {
  local response="$1"
  local needle="$2"
  local label="$3"
  if echo "$response" | grep -q "$needle"; then
    echo "✅ PASS: $label"
  else
    echo "❌ FAIL: $label"
    echo "$response"
    exit 1
  fi
}

RESPONSE=$(post_claim '{"claim_hash":"abc123","truth_claim":true,"claim_status":"PROMOTED"}')
expect_contains "$RESPONSE" "PROTOCOL_VIOLATION" "Promotion rejected"

RESPONSE=$(post_claim '{"claim_hash":"abc123","_promote":true}')
expect_contains "$RESPONSE" "PROTOCOL_VIOLATION" "Undefined promotion rejected"

RESPONSE=$(post_claim '{"claim_hash":"abc123","claim_status":"PROMOTED","truth_claim":false}')
expect_contains "$RESPONSE" "PROTOCOL_VIOLATION" "Status promotion rejected"

RESPONSE=$(post_claim '{"claim_hash":"abc123","metadata":{"claim_status":"PROMOTED"},"claim_status":"UNPROMOTED","truth_claim":false,"verified_wire_reference":"wire-xyz-789"}')
expect_contains "$RESPONSE" "PROTOCOL_VIOLATION" "Nested promotion blocked"

RESPONSE=$(post_claim '{"claim_hash":"abc123","claim_status":"PROMOTED\"; DROP TABLE claims; --","truth_claim":false}')
expect_contains "$RESPONSE" "PROTOCOL_VIOLATION" "Injection blocked"

RESPONSE=$(post_claim '{"claim_hash":"abc123","claim_status":"UNPROMOTED","truth_claim":false,"verified_wire_reference":"wire-xyz-789"}')
expect_contains "$RESPONSE" "CLAIM_UNPROMOTED" "Valid UNPROMOTED claim accepted"

echo "─────────────────────────────────────────────"
echo "✅ ALL 6 PASS — Claim Firewall hardened."
echo "📜 DOCKET_60_PASSED"
