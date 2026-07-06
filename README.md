# ReceiptOS Base

Replayable verification and receipt infrastructure for onchain and public evidence.

## Current milestone

**RECEIPT-001 — Front Door Shipped** ✅

➡️ Start here: [`RECEIPT-001.md`](./RECEIPT-001.md)

## Philosophy

A receipt records something that can be independently verified. If it cannot be independently verified, it is not a receipt.

## Current focus

Current focus: **RECEIPT-003 — Canonical Replay Engine**

See:

- [`RECEIPT-001.md`](./RECEIPT-001.md)
- GitHub Issue `#92` — artifact completeness
- GitHub Issue `#93` — replay engine implementation

## Observable receipt roadmap

| Receipt | Observation | Depends on | Status |
|---|---|---|---|
| RECEIPT-001 | Front door shipped | Git commits | ✅ |
| RECEIPT-002 | `jaywisdom.base.eth` resolves | DNS/ENS state | ⏳ |
| RECEIPT-003 | Replay engine implemented | Source code + tests | ⏳ |
| RECEIPT-004 | Replay succeeds on real data | Engine + receipt dataset | ⏳ |
| RECEIPT-005 | Independent reproduction | Another operator | ⏳ |

## Repository purpose

ReceiptOS Base is a public verification project for replayable evidence.

Current status:

- ✅ Public front door
- ✅ Verification artifacts
- ⏳ Canonical replay engine
- ⏳ Automated replay

Authority remains **FALSE**. Evidence can strengthen; authority does not become true.

## Existing verifier paths

This repository also contains earlier verifier and replay work, including:

- `scripts/verify-60-second.js`
- `ReplayBoard/verify_settle_ledger.py`
- `scripts/receiptos.js`
- Farcaster manifest verification tooling

These remain part of the repository history. The root receipt state above is the current public project entry point.
