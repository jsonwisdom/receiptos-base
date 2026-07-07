#!/usr/bin/env bash
set -euo pipefail

ANCHORS_JSON="${1:-evidence/anchors.json}"
REQUIRE_ONCHAIN="${REQUIRE_ONCHAIN:-0}"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

pass() {
  echo "PASS: $*"
}

command -v jq >/dev/null || fail "jq required"
[ -f "$ANCHORS_JSON" ] || fail "missing anchors manifest: $ANCHORS_JSON"

COUNT="$(jq '.anchors | length' "$ANCHORS_JSON")"
[ "$COUNT" -gt 0 ] || fail "anchors manifest has no anchors"

for i in $(seq 0 $((COUNT - 1))); do
  NAME="$(jq -r ".anchors[$i].name" "$ANCHORS_JSON")"
  TYPE="$(jq -r ".anchors[$i].type" "$ANCHORS_JSON")"
  RECEIPT="$(jq -r ".anchors[$i].receipt" "$ANCHORS_JSON")"
  MONITOR="$(jq -r ".anchors[$i].monitor_revocation" "$ANCHORS_JSON")"

  echo "ANCHOR[$i]: $NAME"

  [ "$TYPE" = "eas" ] || fail "$NAME unsupported anchor type: $TYPE"
  [ -f "$RECEIPT" ] || fail "$NAME missing receipt: $RECEIPT"

  scripts/verify-eas-anchor.sh "$RECEIPT"

  if [ "$MONITOR" = "true" ]; then
    if [ -n "${BASE_RPC_URL:-}" ]; then
      scripts/check-eas-revocation.sh "$RECEIPT"
    elif [ "$REQUIRE_ONCHAIN" = "1" ]; then
      fail "$NAME requires BASE_RPC_URL for on-chain revocation check"
    else
      echo "SKIP: $NAME on-chain revocation check; BASE_RPC_URL not set"
    fi
  fi

  pass "$NAME verified"
done

echo "PASS all anchors verified: $COUNT"
