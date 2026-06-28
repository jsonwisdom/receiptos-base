#!/usr/bin/env bash
set -euo pipefail

EXPECTED_HASH="0xdf0e9e385ad3f3ad610f3e4cae6506ab2c83fa5beb75dd921402070c4a80603f"

echo "ROUND_020 Replay Starting..."

python3 verify.py --proof proofs/proof.json > receipts/replayed-receipt.json
python3 receipt_anchor.py receipts/source-receipt.json > receipts/replayed-anchor.json

ACTUAL_HASH="$(python3 - <<'PY'
import json
p=json.load(open("receipts/replayed-anchor.json"))
print(p["receipt_hash"])
PY
)"

echo "Receipt hash: $ACTUAL_HASH"
echo "Expected hash: $EXPECTED_HASH"

if [ "$ACTUAL_HASH" = "$EXPECTED_HASH" ]; then
  echo "EAS match check: PASS"
  echo "ROUND_020 REPLAY: PASS"
else
  echo "EAS match check: FAIL"
  echo "ROUND_020 REPLAY: FAIL"
  exit 1
fi
