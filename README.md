# receiptos-base

![Replay Gate](https://img.shields.io/badge/replay--gate-v1-green)

ReceiptOS: Onchain verifiable receipt + replay engine on Base. Evidence-first verification.

## Install the ReceiptOS verifier

```bash
npm install -g @jsonwisdom/receiptos-verifier
```

CLI aliases:

```bash
receiptos verify <uid> --json
receiptos-verifier verify <uid> --json
```

Boundary: the npm package is a verifier. It does not grant runtime authority, make truth claims, or promote observations beyond `authority=false` evidence checks.

## Verify this receipt in 60 seconds

This is the smallest public proof path in the repo: one sample receipt, one verifier command, one expected PASS line.

Run from the repository root:

```bash
node scripts/verify-60-second.js
```

Expected output includes:

```text
artifact_sha256=PASS
receipt_core_hash=PASS
authority_false=PASS
witness_only_true=PASS
truth_claim_false=PASS
anchor_commit_present=PASS
computed_artifact_sha256=2757b42eff5ffe183315cff32bcf5e2e7420c96c192e463421e59a441b852032
computed_receipt_core_hash=776021ffc8f70ff10f31911a7aaa9eb9ae9fc805d21e29eca591a6e36879be5c
RECEIPTOS_60_SECOND_VERIFY=PASS
```

Sample receipt:

```text
examples/verify-60-second/receipt.sample.json
```

Public commit anchor used by the sample receipt:

```text
80be15969a980db3db2d0628179b89d93c78e9a9
```

Boundary: this demo verifies local receipt binding, canonical receipt hashing, and authority-neutral flags. It does not claim legal truth, runtime authority, or EAS finality. External attestations should be attached as second-stage receipt pointers, not included inside the canonical receipt hash.

## Verify the on-chain ReceiptOS anchor

Packet #007 adds a UID verifier for the dedicated ReceiptOS EAS schema.

Run:

```bash
node scripts/receiptos.js verify 0xd64a416d76f61c412e2a074a8ff26b03231166890be4356cbfc92a657a03ffa6 \
  --json \
  --tx-hash 0x95048e055087326f40600c2de5cb3c687307b466e08fa10fc9e6d57075b8ae8f
```

Expected terminal behavior:

```text
exit code 0
status = PASS
authority = false
```

The verifier checks the decoded EAS payload against the known ReceiptOS anchor:

```text
schema          RECEIPTOS-ANCHOR-001
schema_uid      0x5a535b9ba95c0a8fd86eac8a6db8b75d79213b388a4c25f17b066cc6543d0aa3
repository      jsonwisdom/receiptos-base
merge_commit    95d06d09b0b1ab6896d147ea35d8d235eec7747f
receipt_hash    0x776021ffc8f70ff10f31911a7aaa9eb9ae9fc805d21e29eca591a6e36879be5c
artifact_hash   0x2757b42eff5ffe183315cff32bcf5e2e7420c96c192e463421e59a441b852032
```

JSON contract:

```text
docs/receiptos-cli-json-contract.md
```

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
