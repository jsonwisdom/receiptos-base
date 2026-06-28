#!/usr/bin/env bash
set -euo pipefail

ANCHOR_JSON="${1:-evidence/receipts/eas-global-forest-anchor.json}"
CANONICAL_RECEIPT="evidence/receipts/global-forest-verification.json"
EAS_GRAPHQL_URL="${EAS_GRAPHQL_URL:-https://base.easscan.org/graphql}"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

pass() {
  echo "PASS: $*"
}

command -v jq >/dev/null || fail "jq required"
command -v sha256sum >/dev/null || fail "sha256sum required"
command -v curl >/dev/null || fail "curl required"

[ -f "$ANCHOR_JSON" ] || fail "missing anchor receipt: $ANCHOR_JSON"
[ -f "$CANONICAL_RECEIPT" ] || fail "missing canonical receipt: $CANONICAL_RECEIPT"

ANCHOR_UID="$(jq -r '.uid' "$ANCHOR_JSON")"
LOCAL_FOREST_ROOT="$(jq -r '.forest_root' "$ANCHOR_JSON")"
LOCAL_RECEIPT_HASH="$(jq -r '.receipt_hash' "$ANCHOR_JSON")"
LOCAL_AUTHORITY="$(jq -r '.authority' "$ANCHOR_JSON")"
LOCAL_ROOT_MATCH="$(jq -r '.root_match' "$ANCHOR_JSON")"
LOCAL_REVOCABLE="$(jq -r '.revocable' "$ANCHOR_JSON")"

COMPUTED_HASH="0x$(sha256sum "$CANONICAL_RECEIPT" | awk '{print $1}')"
[ "$LOCAL_RECEIPT_HASH" = "$COMPUTED_HASH" ] || fail "receipt_hash mismatch: local=$LOCAL_RECEIPT_HASH computed=$COMPUTED_HASH"
pass "local receipt_hash matches canonical receipt"

[[ "$ANCHOR_UID" =~ ^0x[0-9a-fA-F]{64}$ ]] || fail "bad uid format"
[[ "$LOCAL_FOREST_ROOT" =~ ^0x[0-9a-fA-F]{64}$ ]] || fail "bad forest_root format"
[[ "$LOCAL_RECEIPT_HASH" =~ ^0x[0-9a-fA-F]{64}$ ]] || fail "bad receipt_hash format"

QUERY='query Attestation($id: String!) { attestation(where: { id: $id }) { id schemaId attester recipient revocable revocationTime data txid } }'
PAYLOAD="$(jq -n --arg query "$QUERY" --arg id "$ANCHOR_UID" '{query:$query, variables:{id:$id}}')"
RESPONSE="$(curl -fsS -H 'content-type: application/json' --data "$PAYLOAD" "$EAS_GRAPHQL_URL")" || fail "EAS GraphQL request failed"

if echo "$RESPONSE" | jq -e '.errors' >/dev/null; then
  echo "$RESPONSE" | jq -c '.errors' >&2
  fail "EAS GraphQL returned errors"
fi

ATTESTATION_ID="$(echo "$RESPONSE" | jq -r '.data.attestation.id // empty')"
[ -n "$ATTESTATION_ID" ] || fail "attestation not found: $ANCHOR_UID"
[ "${ATTESTATION_ID,,}" = "${ANCHOR_UID,,}" ] || fail "uid mismatch: chain=$ATTESTATION_ID local=$ANCHOR_UID"
pass "EAS attestation exists"

CHAIN_REVOCABLE="$(echo "$RESPONSE" | jq -r '.data.attestation.revocable')"
CHAIN_REVOCATION_TIME="$(echo "$RESPONSE" | jq -r '.data.attestation.revocationTime')"
CHAIN_DATA="$(echo "$RESPONSE" | jq -r '.data.attestation.data')"

[ "$CHAIN_REVOCABLE" = "$LOCAL_REVOCABLE" ] || fail "revocable mismatch: chain=$CHAIN_REVOCABLE local=$LOCAL_REVOCABLE"
[ "$CHAIN_REVOCATION_TIME" = "0" ] || fail "attestation revoked: revocationTime=$CHAIN_REVOCATION_TIME"
pass "EAS attestation is unrevoked"

EXPECTED_DATA="${LOCAL_FOREST_ROOT#0x}${LOCAL_RECEIPT_HASH#0x}"
EXPECTED_DATA+="0000000000000000000000000000000000000000000000000000000000000000"
EXPECTED_DATA+="0000000000000000000000000000000000000000000000000000000000000001"
EXPECTED_DATA="0x${EXPECTED_DATA,,}"
CHAIN_DATA="${CHAIN_DATA,,}"

[ "$LOCAL_AUTHORITY" = "false" ] || fail "local authority must be false"
[ "$LOCAL_ROOT_MATCH" = "true" ] || fail "local root_match must be true"
[ "$CHAIN_DATA" = "$EXPECTED_DATA" ] || fail "on-chain raw data mismatch"
pass "on-chain data matches local anchor fields"

echo "PASS"
