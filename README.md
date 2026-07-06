# ReceiptOS Base

Replayable verification and receipt infrastructure for onchain and public evidence.

## Current milestone

**RECEIPT-003.7 — Evidence Verification CI Gate Implemented**

Implemented in code. Awaiting observed GitHub Actions run evidence before marking validated.

➡️ Start here: [`RECEIPT-001.md`](./RECEIPT-001.md)

## Philosophy

A receipt records something that can be independently verified. If it cannot be independently verified, it is not a receipt.

Code committed is not the same as proof executed.

## Current focus

Current focus: **Evidence gate validation without fake green**

See:

- [`RECEIPT-001.md`](./RECEIPT-001.md)
- GitHub Issue `#92` — artifact completeness
- GitHub Issue `#93` — replay engine implementation
- GitHub Issue `#95` — Zora COURT creator coin metadata gate, pending review

## Observable receipt roadmap

| Receipt | Observation | Depends on | Status |
|---|---|---|---|
| RECEIPT-001 | Front door shipped | Git commits | complete |
| RECEIPT-002 | `jaywisdom.base.eth` resolves | DNS/ENS state | pending |
| RECEIPT-003 | Canonical replay engine track | Source code + tests | partial |
| RECEIPT-003.5 | GPK Replay Engine MVP | card schema, game state, replay engine, ruleset | implemented |
| RECEIPT-003.6 | Evidence ledger and verification harness | evidence ledger schema and verifier tool | implemented |
| RECEIPT-003.7 | Evidence Verification CI Gate | workflow and payload fixtures | implemented; awaiting workflow-run evidence |
| RECEIPT-004 | `RECEIPT-001` static replay recorded | recorded input and output hashes | recorded |
| RECEIPT-005 | Independent reproduction | another operator | pending |

## Evidence gate status

The evidence verification path exists, but validation requires observed workflow-run artifacts.

Current test fixtures:

- `evidence-payloads/TEST-NEGATIVE-001/metadata.json` — intentionally contains a placeholder and is expected to fail placeholder scan.
- `evidence-payloads/TEST-POSITIVE-001/metadata.json` — clean local payload and is expected to pass.

Do not mark `RECEIPT-003.7` as validated until both outcomes are observed in GitHub Actions:

1. negative fixture fails without mutating `evidence-ledger.json`
2. positive fixture passes and uploads a verification report without mutating `evidence-ledger.json`

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
- Evidence CI gate implemented
- Evidence CI gate validation pending observed workflow results
- Zora COURT artifact pending cryptographic payload

Authority remains **FALSE**. Evidence can strengthen; authority does not become true.

## Existing verifier paths

This repository also contains earlier verifier and replay work, including:

- `scripts/verify-60-second.js`
- `ReplayBoard/verify_settle_ledger.py`
- `scripts/receiptos.js`
- Farcaster manifest verification tooling

These remain part of the repository history. The root receipt state above is the current public project entry point.
