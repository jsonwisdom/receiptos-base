# ReceiptOS Base EAS Schema #1797 Bridge

Status: offline bridge implementation; no onchain attestation created.

## Externally verified schema

- Network: Base
- Chain ID: `8453`
- Schema number: `1797`
- Schema UID: `0xc90097ca9f787edcc5fa2ce0920032abe4c4417cc8356198fa12d397c46a453c`

Exact EAS fields:

1. `receipt_hash bytes32`
2. `lineage_hash bytes32`
3. `previous_receipt_hash bytes32`
4. `subject_hash bytes32`
5. `source_ref_hash bytes32`
6. `created_at uint64`
7. `evidence_state uint8`
8. `retrieval_state uint8`

## State enums

Evidence state:

- `0 = UNRESOLVED`
- `1 = PARTIAL`
- `2 = MATCH`
- `3 = NOT_APPLICABLE`

Retrieval state:

- `0 = COMPLETE`
- `1 = FAILED`
- `2 = AUTH_BLOCKED`
- `3 = BUDGET_EXHAUSTED`
- `4 = NOT_ATTEMPTED`

Unknown enum values fail closed.

## Hash boundaries

`receipt_hash` is derived through the existing `receiptos/core/hash.py` rail. The bridge does not replace or modify that rail.

`lineage_hash = SHA256(canonical_json({"lineage_id": lineage_id}))`

`subject_hash = SHA256(canonical_json(receipt.subject))`

`source_ref_hash = SHA256(canonical_json({"authority_chain": authority_chain, "official_ref": official_ref}))`

`previous_receipt_hash` is a separate EAS field. Genesis uses 32 zero bytes.

The following are separate concepts and MUST NOT be aliased:

- `lineage_hash` != `previous_receipt_hash`
- `evidence_state` != evidence/invariant objects
- `retrieval_state` != root/evidence-set hashes

## Canonicalization and safety

- Existing ReceiptOS restricted canonical JSON rail is authoritative.
- Float values are rejected by the bridge before hashing.
- Optional sealed artifacts can be byte-hash verified before payload emission.
- The bridge is offline only.
- It does not sign or submit attestations.
- It does not fetch chain state.
- It creates no legal or institutional authority.

## CourtListener gate

A CourtListener receipt instance must be materialized separately and supplied to the bridge. The bridge intentionally does not invent a CourtListener receipt object or a missing root-attestation digest.

No Base attestation should be submitted until the receipt instance, source references, lineage identifier, timestamp, states, and any required sealed artifact hashes are validated.
