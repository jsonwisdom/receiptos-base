# EAS_RAIL_NEXT

Status: Draft specification after `RAIL_V1_OPERATIONAL`.

ReceiptOS now has a deterministic replay gate. EAS anchoring must preserve that boundary:

```text
local replay proves the receipt
EAS proves public timestamped existence of the receipt hash
```

## Design Rule

Do not mutate the canonical settlement receipt after attestation.

```text
receipt_hash = deterministic settlement proof
eas_uid      = external attestation pointer
```

EAS metadata belongs in a companion index or second-stage attestation receipt, not inside the original receipt hash.

## Proposed EAS Schema

Schema name:

```text
ReceiptOSReplayRailV1
```

Fields:

```text
bytes32 receiptHash
bytes32 prevReceiptHash
bytes32 ledgerTipHash
string claimId
string canonicalizerVersion
string verifierVersion
string sourceRepo
string sourceRef
uint256 chainId
bool authority
bool truthClaim
bool witnessOnly
```

Recommended values:

```text
authority=false
truthClaim=false
witnessOnly=true
chainId=8453
sourceRepo=jsonwisdom/receiptos-base
sourceRef=replay-gate-v1
```

## Attestation Payload Rule

The payload should bind only stable replay outputs:

```json
{
  "schema_version": "receiptos.eas_payload.v0.1",
  "receipt_hash": "sha256:...",
  "prev_receipt_hash": "sha256:...",
  "ledger_tip_hash": "sha256:...",
  "claim_id": "...",
  "canonicalizer_version": "REPLAYBOARD_SETTLE_V1",
  "verifier_version": "REPLAYBOARD_VERIFY_SETTLE_LEDGER_V1",
  "source_repo": "jsonwisdom/receiptos-base",
  "source_ref": "replay-gate-v1",
  "chain_id": 8453,
  "authority": false,
  "truth_claim": false,
  "witness_only": true
}
```

## Companion Index

Path:

```text
attestations/attestation_index.jsonl
```

Line format:

```json
{
  "schema_version": "receiptos.attestation_index.v0.1",
  "receipt_hash": "sha256:...",
  "network": "base",
  "chain_id": 8453,
  "schema_uid": "0x...",
  "eas_uid": "0x...",
  "tx_hash": "0x...",
  "attested_at": "ISO-8601 timestamp",
  "authority": false,
  "truth_claim": false,
  "witness_only": true
}
```

## Workflow Order

```text
ReplayBoard Settle
  ↓
Deterministic replay gate
  ↓
Extract final receipt_hash
  ↓
Create EAS payload
  ↓
Submit attestation
  ↓
Append attestation_index.jsonl
  ↓
Upload artifacts
```

## Verification Flow

A verifier must:

1. Re-run `ReplayBoard/verify_settle_ledger.py` locally.
2. Extract the final `receipt_hash` from `settle.jsonl`.
3. Read `attestation_index.jsonl`.
4. Fetch the EAS UID from Base.
5. Confirm the on-chain attestation contains the same `receiptHash`.
6. Confirm `authority=false`, `truthClaim=false`, and `witnessOnly=true`.
7. Fail closed if any value drifts.

## Environment Variables

Expected future workflow secrets:

```text
BASE_RPC_URL
EAS_CONTRACT_ADDRESS
EAS_SCHEMA_UID
EAS_ATTESTER_PRIVATE_KEY
```

Optional:

```text
BASESCAN_API_KEY
```

## Implementation Files

Planned:

```text
ReplayBoard/eas_payload.py
ReplayBoard/eas_attest.py
ReplayBoard/verify_eas_attestation.py
attestations/attestation_index.jsonl
```

## Open Decisions

- Confirm EAS contract address on Base.
- Confirm schema UID after schema registration.
- Decide whether every settle is attested or only checkpoint/tip receipts.
- Decide whether GitHub Actions should commit `attestation_index.jsonl` back to repo or upload it as an artifact first.

## Recommended First Implementation

Start artifact-only before auto-commit:

```text
settle.jsonl + evidence.bin + eas_payload.json + attestation_index.jsonl
```

Once stable, allow a separate human-approved commit that appends the attestation index.

Replay first. EAS second. Authority never.
