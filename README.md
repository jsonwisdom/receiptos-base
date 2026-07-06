# ReceiptOS Base

Replayable verification and receipt infrastructure for onchain and public evidence.

## Current milestone

**RECEIPT-003.7 — Evidence Verification CI Gate Validated**

Validated by dual-branch GitHub Actions reports committed as replayable JSON artifacts.

➡️ Start here: [`RECEIPT-001.md`](./RECEIPT-001.md)

## Philosophy

A receipt records something that can be independently verified. If it cannot be independently verified, it is not a receipt.

Code committed is not the same as proof executed. Observed is not verified until the replayable artifact is present.

## Current focus

Current focus: **Evidence gate validation complete; Zora payload gate remains pending**

See:

- [`RECEIPT-001.md`](./RECEIPT-001.md)
- GitHub Issue `#92` — artifact completeness
- GitHub Issue `#93` — replay engine implementation
- GitHub Issue `#95` — Zora COURT creator coin metadata gate, pending review
- `receipts/RECEIPT-003.7-PROMOTION.json` — CI gate validation promotion receipt

## Observable receipt roadmap

| Receipt | Observation | Depends on | Status |
|---|---|---|---|
| RECEIPT-001 | Front door shipped | Git commits | complete |
| RECEIPT-002 | `jaywisdom.base.eth` resolves | DNS/ENS state | pending |
| RECEIPT-003 | Canonical replay engine track | Source code + tests | partial |
| RECEIPT-003.5 | GPK Replay Engine MVP | card schema, game state, replay engine, ruleset | implemented |
| RECEIPT-003.6 | Evidence ledger and verification harness | evidence ledger schema and verifier tool | implemented |
| RECEIPT-003.7 | Evidence Verification CI Gate | workflow, payload fixtures, committed positive and negative reports | validated |
| RECEIPT-004 | `RECEIPT-001` static replay recorded | recorded input and output hashes | recorded |
| RECEIPT-005 | Independent reproduction | another operator | pending |

## Evidence gate status

The evidence verification path is validated by committed workflow report JSONs:

- `evidence-reports/TEST-POSITIVE-001.report.json` — status `VERIFIED`, placeholder scan `PASS`.
- `evidence-reports/TEST-NEGATIVE-001.report.json` — status `REJECTED`, placeholder scan `FAIL`.
- `receipts/RECEIPT-003.7-PROMOTION.json` — records both run IDs, artifact digests, report hashes, and the validation disposition.

Validation does not mutate `evidence-ledger.json` automatically. Ledger promotion remains manual and explicit.

## Zora COURT artifact intake

Issue `#95` tracks artifact `0xe423ae19fffcee95919dde96a31e828bc060e36f`.

Classification: `external_attestation`  
Status: `PENDING_REVIEW`  
Authority: `false`  
Blocked reason: missing canonical payload and content hash

The Zora artifact remains sidecar context only until a recomputable canonical payload is supplied.

## Repository purpose

ReceiptOS Base is a public verification project for replayable evidence.

Current status:

- Public front door complete
- Verification artifacts complete
- GPK replay MVP implemented
- Evidence verification harness implemented
- Evidence CI gate validated
- Zora COURT artifact pending cryptographic payload

Authority remains **FALSE**. Evidence can strengthen; authority does not become true.

## Existing verifier paths

This repository also contains earlier verifier and replay work, including:

- `scripts/verify-60-second.js`
- `ReplayBoard/verify_settle_ledger.py`
- `scripts/receiptos.js`
- Farcaster manifest verification tooling

These remain part of the repository history. The root receipt state above is the current public project entry point.
