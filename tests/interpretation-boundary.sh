#!/bin/bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:3000}"

echo "🧪 Docket #61 — Interpretation Boundary"
echo "─────────────────────────────────────────────"

post_interpret() {
  curl -s -X POST "$BASE_URL/api/interpret" \
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

RESPONSE=$(post_interpret '{"receipt_id":"docket-57-ros-0006","policy":"trust-score-v1","truth_claim":true}')
expect_contains "$RESPONSE" '"truth_claim":false' "truth_claim remains false"

RESPONSE=$(post_interpret '{"receipt_id":"docket-57-ros-0006","policy":"trust-score-v1","authority":true}')
expect_contains "$RESPONSE" '"authority":false' "authority remains false"

RESULT1=$(post_interpret '{"receipt_id":"docket-57-ros-0006","policy":"trust-score-v1"}')
RESULT2=$(post_interpret '{"receipt_id":"docket-57-ros-0006","policy":"trust-score-v1"}')
SCORE1=$(echo "$RESULT1" | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>console.log(JSON.parse(s).interpretation.score))")
SCORE2=$(echo "$RESULT2" | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>console.log(JSON.parse(s).interpretation.score))")
if [ "$SCORE1" = "$SCORE2" ]; then echo "✅ PASS: deterministic"; else echo "❌ FAIL: non-deterministic"; exit 1; fi

RISK=$(post_interpret '{"receipt_id":"docket-57-ros-0006","policy":"risk-v1"}')
RISK_SCORE=$(echo "$RISK" | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>console.log(JSON.parse(s).interpretation.score))")
if [ "$SCORE1" != "$RISK_SCORE" ]; then echo "✅ PASS: different policies yield different scores"; else echo "❌ FAIL: policies not differentiated"; exit 1; fi

RESPONSE=$(post_interpret '{"receipt_id":"nonexistent","policy":"trust-score-v1"}')
expect_contains "$RESPONSE" '"valid":false' "missing receipt fails closed"

RESPONSE=$(post_interpret '{"receipt_id":"docket-57-ros-0006","policy":"unknown-policy"}')
expect_contains "$RESPONSE" '"valid":false' "unknown policy fails closed"

echo "─────────────────────────────────────────────"
echo "✅ ALL 6 PASS — Interpretation boundary hardened."
echo "📜 DOCKET_61_PASSED"
