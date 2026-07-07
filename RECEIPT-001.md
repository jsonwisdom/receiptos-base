# RECEIPT-001 — Front Door Shipped

**Status:** LIVE  
**Date:** 2026-07-06  
**Authority:** FALSE

## Philosophy

A receipt records something that can be independently verified. If it cannot be independently verified, it is not a receipt.

## What exists

The public front door for the Receipts Machine has shipped.

Location:

- `front-door/index.html`
- `front-door/vercel.json`
- `front-door/README.md`
- `front-door/.gitignore`

## Evidence

Repository: `jsonwisdom/receiptos-base`

Commits:

- `49c7aea` — Add Jay Wisdom front door page
- `f3fd153` — Add front door Vercel config
- `53c05d0` — Add front door README
- `9ba9da0` — Add front door gitignore

## Current boundary

Implemented:

- Public landing page
- Project explanation
- Identity surface
- Audit entry point

Not implemented:

- Canonical replay engine (`observation_protocol`)
- Automated receipt ingestion
- Automated replay verification

## How to contribute

Current priorities:

1. Implement the canonical replay engine
2. Improve receipt schemas
3. Expand verification tooling
4. Improve documentation

See GitHub Issues:

- `#92` — Artifact completeness
- `#93` — Replay engine implementation

## Receipts in progress

| Receipt | Observation | Depends on | Status |
|---|---|---|---|
| RECEIPT-001 | Front door shipped | Git commits | ✅ |
| RECEIPT-002 | `jaywisdom.base.eth` resolves | DNS/ENS state | ⏳ |
| RECEIPT-003 | Replay engine implemented | Source code + tests | ⏳ |
| RECEIPT-004 | Replay succeeds on real data | Engine + receipt dataset | ⏳ |
| RECEIPT-005 | Independent reproduction | Another operator | ⏳ |

## Next receipt

**RECEIPT-002 — Front Door Resolves**

Evidence required:

- [ ] Vercel deployment URL is live
- [ ] `jaywisdom.base.eth` points to that deployment
- [ ] Independent browser resolves correctly
- [ ] Links load without manual intervention
- [ ] Receipt committed

Rule: once all five are true, RECEIPT-002 exists. If one is not true yet, it does not.

---

**Verification over narrative.**
