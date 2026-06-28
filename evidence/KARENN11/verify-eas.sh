#!/usr/bin/env bash
set -euo pipefail

: "${BASE_RPC_URL:=https://mainnet.base.org}"
: "${EAS_UID:?Missing EAS_UID}"

eas get-attestation \
  --uid "$EAS_UID" \
  --rpc-url "$BASE_RPC_URL"
