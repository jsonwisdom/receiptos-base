# ROUND_019 Replay Bundle

Purpose: reproduce one verification receipt offline and compare its hash to the EAS anchor.

## Replay

```bash
python3 verify.py --proof proofs/proof.json > receipts/replayed-receipt.json
python3 receipt_anchor.py receipts/source-receipt.json > receipts/replayed-anchor.json
cat attestations/eas-receipt-anchor.txt
