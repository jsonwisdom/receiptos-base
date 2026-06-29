# receiptos-base

ReceiptOS: Onchain verifiable receipt + replay engine on Base. Evidence-first verification.

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
