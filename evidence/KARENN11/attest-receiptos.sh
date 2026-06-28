#!/usr/bin/env bash
set -euo pipefail

: "${BASE_RPC_URL:=https://mainnet.base.org}"
: "${SCHEMA_UID:?Missing SCHEMA_UID}"
: "${PRIVATE_KEY:?Missing PRIVATE_KEY}"

eas attest \
  --schema "$SCHEMA_UID" \
  --data "$(cat eas-payload.json)" \
  --rpc-url "$BASE_RPC_URL" \
  --private-key "$PRIVATE_KEY"
