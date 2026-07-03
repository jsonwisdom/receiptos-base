# receiptos-base

![Replay Gate](https://img.shields.io/badge/replay--gate-v1-green)

ReceiptOS: Onchain verifiable receipt + replay engine on Base. Evidence-first verification.

## Replay Gate v1

`RAIL_V1_OPERATIONAL`

ReplayBoard settlement now has a deterministic verifier gate on `main`.

Milestone commits:

```text
c98a700  Add deterministic ReplayBoard ledger verifier
16445e3  Gate ReplayBoard settle with deterministic verifier
```

Verifier path:

```text
ReplayBoard/verify_settle_ledger.py
```

Workflow path:

```text
.github/workflows/replayboard-settle-probe.yml
```

### Replay Gate Invariants (v1)

- Deterministic replay of the settlement ledger.
- Cryptographic hash chain continuity through `prev_receipt_hash`.
- Strict `evidence.bin` to `receipt.evidence.content_hash` binding.
- `authority=false`, `truth_claim=false`, and `witness_only=true` enforced.
- Canonical receipt hash recomputation before green.
- Verifier fails closed on any violation.

### Canonical Boundary

The canonical receipt hash is computed before any external attestation metadata is attached.

```text
receipt_hash = deterministic settlement proof
eas_uid      = external attestation pointer
```

Do not include `eas_uid` inside the original `receipt_hash` unless creating a second-stage attestation receipt.

### Local Replay Gate

```bash
python ReplayBoard/verify_settle_ledger.py \
  --ledger /tmp/replayboard/settle.jsonl \
  --raw-evidence /tmp/replayboard-evidence/evidence.bin
```

Expected output:

```text
REPLAYBOARD_REPLAY_GATE=PASS
```

Replay decides. Receipt doesn't lie.

## Farcaster Mini App Manifest Verification

This repository includes a replay-safe Farcaster Mini App identity stack for `JAYWISDOM`.

### Identity artifacts

```text
.well-known/farcaster/manifest.json
.well-known/farcaster/manifest.jcs
.well-known/farcaster/manifest.lock.json
```

- `manifest.json` is the human-readable source manifest.
- `manifest.jcs` is the canonical byte representation used for hashing.
- `manifest.lock.json` binds the canonical manifest to a registered SHA-256 digest.

### Verification doctrine

The CI membrane follows this order:

```text
Schema / Source
      ↓
Semantic verifier
      ↓
Canonical bytes
      ↓
Manifest lock
      ↓
CI receipt
```

### Semantic verifier

Run locally:

```bash
node scripts/semantic-verify.js
```

The verifier enforces:

- stable lowercase manifest `id`
- no empty strings anywhere in the manifest
- HTTPS-only URLs for developer, website, app, icon, and screenshots
- PNG icon requirement
- screenshot presence and image URL checks
- Farcaster permission whitelist
- `manifest.json` to `manifest.jcs` canonical drift detection
- lock drift checks for manifest id, canonicalization, canonical source, timestamp, authority, and SHA-256

### Manifest lock verifier

Run locally:

```bash
node scripts/verify-manifest-lock.js
```

The lock verifier confirms that `.well-known/farcaster/manifest.jcs` hashes to the SHA-256 recorded in `.well-known/farcaster/manifest.lock.json`.

### Doctrine

This stack does not claim authority. It records replayable evidence.

```text
authority=false
Replay First. Verify Everything.
```
