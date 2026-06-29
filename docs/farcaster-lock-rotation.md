# Farcaster Manifest Lock Rotation Runbook

This runbook defines the deterministic procedure for changing the JAYWISDOM Farcaster Mini App manifest.

The doctrine is simple:

```text
manifest.json -> RFC8785 canonicalize -> manifest.jcs -> sha256 -> manifest.lock.json
```

Do not edit `manifest.jcs` or `manifest.lock.json` by hand unless you are deliberately rotating the manifest lock.

## When to rotate

Rotate the lock whenever any field in `.well-known/farcaster/manifest.json` changes.

Examples:

- app URL change
- icon URL change
- screenshot URL change
- permission change
- developer metadata change
- description change

## Rotation steps

### 1. Edit the source manifest

Update:

```text
.well-known/farcaster/manifest.json
```

Keep required fields non-empty and HTTPS-only where required.

### 2. Regenerate canonical JCS bytes

Use the same RFC8785 canonicalizer used by CI:

```bash
node - <<'NODE' > .well-known/farcaster/manifest.jcs
const fs = require('fs');
const { canonicalize } = require('json-canonicalize');
const manifest = JSON.parse(fs.readFileSync('.well-known/farcaster/manifest.json', 'utf8'));
process.stdout.write(canonicalize(manifest));
NODE
```

### 3. Compute the canonical SHA-256

```bash
SHA256=$(sha256sum .well-known/farcaster/manifest.jcs | awk '{print $1}')
echo "$SHA256"
```

### 4. Update the lock file

Update:

```text
.well-known/farcaster/manifest.lock.json
```

Required lock fields:

```json
{
  "manifest_id": "jaywisdom",
  "manifest_path": ".well-known/farcaster/manifest.jcs",
  "canonical_source": "manifest.jcs",
  "canonicalization": "RFC8785",
  "sha256": "<NEW_SHA256>",
  "created_at": "<UTC_ISO_8601_TIMESTAMP>",
  "status": "LOCKED",
  "authority": false
}
```

Rules:

- `sha256` must match `manifest.jcs` exactly.
- `created_at` must not be future-dated.
- `authority` must remain `false`.
- `canonicalization` must remain `RFC8785`.

### 5. Run local verification

```bash
npm install
npm run verify:farcaster
```

This runs:

```text
RFC8785 test vectors
semantic verifier
manifest lock verifier
```

### 6. Commit the rotation

```bash
git add .well-known/farcaster/manifest.json \
        .well-known/farcaster/manifest.jcs \
        .well-known/farcaster/manifest.lock.json

git commit -m "rotate Farcaster manifest lock"
git push
```

CI must pass before the rotated manifest is considered valid.

## Unicode policy

RFC8785/JCS provides deterministic serialization. It does not normalize Unicode.

That means these two visually similar strings hash differently:

```text
é        U+00E9
 e + ´   U+0065 U+0301
```

Policy:

- Do not rely on JCS to normalize human-readable text.
- Prefer NFC-normalized text when editing `manifest.json`.
- Treat the exact manifest bytes as the source of truth.
- If Unicode text changes form, rotate the lock because the canonical SHA-256 will change.

## Doctrine

This process records replayable evidence. It does not assert authority.

```text
authority=false
Replay First. Verify Everything.
```
