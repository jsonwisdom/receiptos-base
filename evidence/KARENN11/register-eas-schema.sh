#!/usr/bin/env bash
set -euo pipefail

: "${BASE_RPC_URL:=https://mainnet.base.org}"

eas schema-register \
  "string artifact,string network,address contractAddress,bytes32 creationTx,string metadataCID,string mediaCID,bytes32 sha256Metadata,bytes32 sha256Media,bytes32 sha256Bundle,string gitCommit,bool replayable,bool authority" \
  "0x0000000000000000000000000000000000000000" \
  --rpc-url "$BASE_RPC_URL"
