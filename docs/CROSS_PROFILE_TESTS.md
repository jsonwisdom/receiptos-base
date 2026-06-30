# Cross-Profile Tests

## RP-002: ReceiptOS + EAS v1

This test proves that the strict ReceiptOS / ESG-001 base validator can remain representation-only while an application profile validates EAS-specific shape above it.

## Command

```bash
python tools/validate_eas_profile_frame.py fixtures/rp-002-eas-frame.example.json --disable-timestamp
```

## Expected result

```json
{
  "authority": false,
  "base_conformant": true,
  "base_errors": [],
  "conformant": true,
  "eas_profile_valid": true,
  "profile_errors": [],
  "truth_claim": false
}
```

## Boundary

The EAS profile validator checks only:

- base ReceiptOS conformance
- `payload.profile == receiptos-eas-v1`
- `artifact_hash` shape as an opaque profile claim
- EAS UID / schema / transaction hash shape
- optional EAS contract address shape
- `signature.profile == eas-attestation-v1`

It does not perform:

- on-chain lookup
- EAS contract verification
- artifact canonicalization
- truth adjudication
- authority promotion
- graph-derived state mutation

The base validator remains unchanged and strict.
