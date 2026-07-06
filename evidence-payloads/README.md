# Evidence Payload Intake

This folder is for cryptographic payloads that can be verified by `tools/evidence_verify.py`.

Court rule:

```text
No Payload = No Verification
No Receipt = No Authority
Authority remains false
```

## Folder format

Create one folder per evidence receipt:

```text
evidence-payloads/ZORA-e423ae19fffcee95919dde96a31e828bc060e36f/
├── manifest.env
└── metadata.json
```

## manifest.env

```bash
TOKEN_URI="TOKEN_URI_HERE"
ARTIFACT_ID="0xe423ae19fffcee95919dde96a31e828bc060e36f"
RECEIPT_ID="ZORA-e423ae19fffcee95919dde96a31e828bc060e36f"
```

## metadata.json

Use the raw metadata JSON returned by the token URI, RPC call, creator export, or immutable metadata source.

Do not paste courtroom prose, page summaries, holder counts, ticker descriptions, or marketplace observations as `metadata.json` unless that text is the exact canonical metadata payload.

## Local verification

```bash
python3 tools/evidence_verify.py \
  --payload evidence-payloads/ZORA-e423ae19fffcee95919dde96a31e828bc060e36f/metadata.json \
  --token-uri "TOKEN_URI_HERE" \
  --artifact-id 0xe423ae19fffcee95919dde96a31e828bc060e36f \
  --receipt-id ZORA-e423ae19fffcee95919dde96a31e828bc060e36f
```

## CI behavior

The GitHub workflow `.github/workflows/evidence-verify.yml` scans every `evidence-payloads/*/metadata.json` file with its sibling `manifest.env`.

If no payload exists, CI exits cleanly and the artifact remains `PENDING_REVIEW`.

If payload exists and verification passes, CI uploads a JSON report as an artifact. The ledger still must be updated intentionally; CI does not silently mutate `evidence-ledger.json`.
