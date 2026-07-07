# PRC-JRN-FIELD-EXT-001 Intake Template

Status: open
Version: 1.0.0
Authority: false
Purpose: first authentic external participant payload
Reserved slot: EXT-001
Synthetic substitution: prohibited

## Invariant

EXT-001 is reserved for the first real participant artifact. Synthetic validation artifacts, facilitator summaries, rewritten responses, or reconstructed notes must not occupy this slot.

## Constitutional Boundary

GREEN means receipt verified, hash matches, replay succeeds, and authority remains false.

GREEN does not mean the underlying claim is true.

Timestamp, not tribunal.

EXT-001 records provenance and replay status only. It does not create truth authority.

## Intake Record

Receipt ID: PRC-JRN-FIELD-EXT-001
Participant ID:
Case ID:
Captured At UTC:
Raw Payload SHA-256:
Append-Only Freeze Ref:
Facilitator Notes Ref:
Public Ledger Pointer:
Index Status: pending
Authority: false

## Raw Participant Payload

Paste the participant output exactly as received below this line. Do not correct spelling, grammar, formatting, links, timestamps, or reasoning.

--- RAW START ---


--- RAW END ---

## Facilitator Notes Rule

Facilitator notes must be stored separately and referenced only by pointer. Notes may describe intake conditions, consent, session context, or anomalies, but they must not be merged into the raw participant payload.

## Capture Protocol

1. Capture raw participant output exactly as received.
2. Compute SHA-256 over the preserved raw payload.
3. Freeze the raw artifact append-only.
4. Register receipt as PRC-JRN-FIELD-EXT-001.
5. Update the public index or ledger pointer.
6. Run synthesis only against the verified frozen original.

## ACTIVE_LANES Transition

Before verified EXT-001 receipt:

```text
LANE=PRC-JRN-EXT-001
STATUS=YELLOW
STATUS_SOURCE=REPORTED
RECEIPT_PTR=NULL
```

After verified EXT-001 receipt:

```text
LANE=PRC-JRN-EXT-001
STATUS=GREEN
STATUS_SOURCE=VERIFIED_RECEIPT
RECEIPT_PTR=sha256:<computed_hash>
```

This makes the YELLOW to GREEN transition explicit, replayable, and bound to a single SHA-256 pointer. Authority remains false.

## Rejection Conditions

Reject or mark disputed if:

- the payload is synthetic,
- the participant artifact was rewritten before capture,
- facilitator notes are mixed into raw output,
- the hash cannot be reproduced,
- the freeze pointer is missing,
- authority is set to true,
- GREEN is used as a truth claim instead of a provenance and replay signal.

## Completion Gate

EXT-001 is complete only when the raw artifact, digest, freeze reference, receipt record, and public ledger pointer are present and reproducible.
