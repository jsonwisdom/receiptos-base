# ReceiptOS CLI JSON Contract v1.1

Packet #007 introduces a stable JSON output contract for the ReceiptOS verifier.

## Command

```bash
node scripts/receiptos.js verify 0xd64a416d76f61c412e2a074a8ff26b03231166890be4356cbfc92a657a03ffa6 \
  --json \
  --tx-hash 0x95048e055087326f40600c2de5cb3c687307b466e08fa10fc9e6d57075b8ae8f
```

## Exit codes

```text
0 = PASS
1 = FAIL
2 = PENDING / unavailable / malformed input
```

## PASS output shape

```json
{
  "status": "PASS",
  "authority": false,
  "uid": "0xd64a416d76f61c412e2a074a8ff26b03231166890be4356cbfc92a657a03ffa6",
  "tx_hash": "0x95048e055087326f40600c2de5cb3c687307b466e08fa10fc9e6d57075b8ae8f",
  "schema": "RECEIPTOS-ANCHOR-001",
  "schema_uid": "0x5a535b9ba95c0a8fd86eac8a6db8b75d79213b388a4c25f17b066cc6543d0aa3",
  "repository": "jsonwisdom/receiptos-base",
  "merge_commit": "95d06d09b0b1ab6896d147ea35d8d235eec7747f",
  "receipt_core_hash": "0x776021ffc8f70ff10f31911a7aaa9eb9ae9fc805d21e29eca591a6e36879be5c",
  "artifact_sha256": "0x2757b42eff5ffe183315cff32bcf5e2e7420c96c192e463421e59a441b852032",
  "decoded_payload": {
    "protocol": "RECEIPTOS-ANCHOR-001",
    "project": "receiptos-base",
    "repository": "jsonwisdom/receiptos-base",
    "merge_commit": "95d06d09b0b1ab6896d147ea35d8d235eec7747f",
    "receipt_core_hash": "0x776021ffc8f70ff10f31911a7aaa9eb9ae9fc805d21e29eca591a6e36879be5c",
    "artifact_sha256": "0x2757b42eff5ffe183315cff32bcf5e2e7420c96c192e463421e59a441b852032",
    "demo": "verify-60-second",
    "authority": false,
    "version": "1.0.0",
    "parent_receipt": "0x0000000000000000000000000000000000000000000000000000000000000000"
  },
  "checks": {
    "uid_resolved": true,
    "schema_match": true,
    "recipient_match": true,
    "protocol_match": true,
    "project_match": true,
    "repository_match": true,
    "commit_match": true,
    "receipt_hash_match": true,
    "artifact_hash_match": true,
    "demo_match": true,
    "authority_false": true,
    "version_match": true,
    "parent_receipt_zero": true
  }
}
```

## Boundary

The CLI verifies process provenance for the ReceiptOS 60-second demo. It does not assert legal truth, factual truth outside the decoded attestation, or authority.

```text
authority=false
```
