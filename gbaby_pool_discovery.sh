#!/usr/bin/env bash
set -euo pipefail

RPC="${RPC:-https://mainnet.base.org}"
START="${START:-49250000}"
END="${END:-49256000}"

POOL_MANAGER="0x498581ff718922c3f8e6a244956af099b2652b2b"
TOKEN="0x8894e88310d46fb19ad3e309455248aeeab81800"
OUT="GB-S1_POOL_DISCOVERY_BASE"

mkdir -p "$OUT"

rpc() {
  curl -sS "$RPC" \
    -H 'content-type: application/json' \
    --data "$1"
}

echo "1/5 — Verifying Base chain..."

CHAIN_HEX=$(rpc \
'{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' |
jq -r '.result')

CHAIN_ID=$((CHAIN_HEX))

if [ "$CHAIN_ID" -ne 8453 ]; then
  echo "FAIL: Expected Base chain ID 8453; received $CHAIN_ID"
  exit 1
fi

TOPIC0=$(
python3 - <<'PY'
from Crypto.Hash import keccak
k = keccak.new(digest_bits=256)
k.update(
 b"Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)"
)
print("0x" + k.hexdigest())
PY
)

printf -v START_HEX '0x%x' "$START"
printf -v END_HEX '0x%x' "$END"

echo "2/5 — Fetching Initialize logs..."

QUERY=$(jq -n \
  --arg address "$POOL_MANAGER" \
  --arg from "$START_HEX" \
  --arg to "$END_HEX" \
  --arg topic "$TOPIC0" \
'{
 jsonrpc:"2.0",
 id:1,
 method:"eth_getLogs",
 params:[{
   address:$address,
   fromBlock:$from,
   toBlock:$to,
   topics:[$topic]
 }]
}')

rpc "$QUERY" > "$OUT/initialize_rpc_response.json"

jq -e '.error == null' \
"$OUT/initialize_rpc_response.json" >/dev/null || {
  jq '.error' "$OUT/initialize_rpc_response.json"
  echo "RPC rejected the block range."
  exit 1
}

jq '.result' \
"$OUT/initialize_rpc_response.json" \
> "$OUT/initialize_all_raw.json"

echo "3/5 — Filtering GBABY pools..."

python3 - \
"$OUT/initialize_all_raw.json" \
"$OUT/initialize_matches.json" \
"$TOKEN" <<'PY'
import json
import sys

src, dst, token = sys.argv[1:]
token = token.lower().removeprefix("0x")
logs = json.load(open(src))
matches = []

def addr(topic):
    return "0x" + topic[-40:].lower()

def word(data, i):
    raw = data.removeprefix("0x")
    return int(raw[i*64:(i+1)*64], 16)

def signed(value, bits):
    if value >= 1 << (bits - 1):
        return value - (1 << bits)
    return value

for log in logs:
    topics = log.get("topics", [])
    if len(topics) < 4:
        continue

    currency0 = addr(topics[2])
    currency1 = addr(topics[3])

    if token not in (currency0[2:], currency1[2:]):
        continue

    data = log["data"]

    matches.append({
        "transaction_hash": log["transactionHash"],
        "block_number": int(log["blockNumber"], 16),
        "log_index": int(log["logIndex"], 16),
        "pool_id": topics[1],
        "currency0": currency0,
        "currency1": currency1,
        "fee": word(data, 0) & ((1 << 24) - 1),
        "tick_spacing": signed(
            word(data, 1) & ((1 << 24) - 1), 24
        ),
        "hooks": "0x" + format(word(data, 2), "040x")[-40:],
        "sqrt_price_x96_initial": str(word(data, 3)),
        "initial_tick": signed(
            word(data, 4) & ((1 << 24) - 1), 24
        )
    })

json.dump(matches, open(dst, "w"), indent=2)
print("Matches found:", len(matches))
PY

echo "4/5 — Capturing block anchor..."

BLOCK_QUERY=$(jq -n --arg block "$END_HEX" \
'{
 jsonrpc:"2.0",
 id:1,
 method:"eth_getBlockByNumber",
 params:[$block,false]
}')

rpc "$BLOCK_QUERY" > "$OUT/end_block.json"

END_HASH=$(jq -r \
'.result.hash // "UNAVAILABLE"' \
"$OUT/end_block.json")

UTC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$OUT/operator_receipt.json" <<JSON
{
  "schema": "PoolDiscoveryReceipt",
  "version": "1.0",
  "status": "PARTIAL",
  "mode": "EVIDENCE_ONLY",
  "inference": "DISABLED",
  "chain": "Base",
  "chain_id": 8453,
  "pool_manager": "$POOL_MANAGER",
  "anchor_token": "$TOKEN",
  "scan_start_block": $START,
  "scan_end_block": $END,
  "end_block_hash": "$END_HASH",
  "query_timestamp_utc": "$UTC",
  "next_gate": "POOLKEY_IDENTIFIED"
}
JSON

echo "5/5 — Hashing and packaging..."

(
  cd "$OUT"
  sha256sum *.json > SHA256SUMS.txt
)

tar -czf "${OUT}.tar.gz" "$OUT"

echo
echo "=== MATCHES ==="
jq . "$OUT/initialize_matches.json"

echo
echo "=== PACKAGE ==="
ls -lh "${OUT}.tar.gz"
