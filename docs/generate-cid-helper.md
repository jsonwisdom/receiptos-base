# generate_cid_helper.py

Deterministic helper for comparing local metadata JSON against declared CID/hash data in provenance or bridge records.

## Boundary

This helper does not mutate ledgers and does not grant authority.

It emits a replayable JSON report with:

- raw file `content_hash`
- canonical JSON `canonical_hash`
- expected CID
- expected metadata hash
- bridge/provenance comparison checks
- `authority: false`

## Basic usage

```bash
python3 tools/generate_cid_helper.py \
  --metadata provenance/dni-gross-intel-crew-genesis-verify-v1.json \
  --provenance provenance/dni-gross-intel-crew-genesis-verify-v1.json \
  --artifact-id 0xe423ae19fffcee95919dde96a31e828bc060e36f
```

## With explicit expected CID/hash

```bash
python3 tools/generate_cid_helper.py \
  --metadata metadata.json \
  --expected-cid bafkreig6du4jfapxzqvsk2gftdfwoim7kodnsgtbt2jspp6kufm732msze \
  --expected-metadata-hash 0xde1d389281f7cc2b2568c598cb67219f5386d91a619e9327bfcaa159fde992c9 \
  --provenance provenance/dni-gross-intel-crew-genesis-verify-v1.json \
  --artifact-id 0xe423ae19fffcee95919dde96a31e828bc060e36f
```

## Status meaning

- `VERIFIED`: available comparison targets all match either the raw content hash or canonical JSON hash.
- `BLOCKED`: comparison target is missing or mismatch detected.

CID recomputation is conservative. The helper compares declared CID values; it does not claim to recompute IPFS CID bytes without an explicit CID library.
