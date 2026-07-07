# Farcaster Manifest Transparency Log Runbook

This runbook defines how to publish the JAYWISDOM Farcaster Mini App manifest lock hash to an append-only transparency log.

The goal is tamper evidence, not authority.

```text
authority=false
lock.sha256 -> transparency log -> replayable inclusion proof
```

## What gets logged

Log the canonical manifest lock hash from:

```text
.well-known/farcaster/manifest.lock.json
```

Field:

```text
sha256
```

Current doctrine:

```text
manifest.json -> RFC8785 canonicalize -> manifest.jcs -> sha256 -> manifest.lock.json -> transparency log
```

## Recommended tool

Use Sigstore Rekor for public transparency logging.

Rekor does not decide truth. It records that a digest existed at a point in time.

## Manual logging flow

### 1. Verify locally first

```bash
npm install
npm run verify:farcaster
```

Do not log a manifest hash unless local verification passes.

### 2. Extract the lock hash

```bash
LOCK_SHA256=$(node -e "const fs=require('fs'); const lock=JSON.parse(fs.readFileSync('.well-known/farcaster/manifest.lock.json','utf8')); console.log(lock.sha256)")
echo "$LOCK_SHA256"
```

### 3. Create a digest file

```bash
mkdir -p .receipts/transparency
printf "%s" "$LOCK_SHA256" > .receipts/transparency/farcaster-manifest-lock.sha256
```

### 4. Upload to Rekor

Example using Rekor CLI:

```bash
rekor-cli upload \
  --artifact .receipts/transparency/farcaster-manifest-lock.sha256
```

Capture the returned log index, UUID, integrated time, and inclusion proof.

### 5. Save a local receipt

Create:

```text
.receipts/transparency/farcaster-manifest-rekor-receipt.json
```

Recommended receipt shape:

```json
{
  "receipt_type": "FARCASTER_MANIFEST_REKOR_RECEIPT_V1",
  "manifest_id": "jaywisdom",
  "lock_sha256": "<LOCK_SHA256>",
  "canonicalization": "RFC8785",
  "rekor_uuid": "<REKOR_UUID>",
  "rekor_log_index": "<LOG_INDEX>",
  "integrated_time": "<INTEGRATED_TIME>",
  "git_commit": "<GIT_COMMIT>",
  "authority": false
}
```

### 6. Commit the receipt

```bash
git add .receipts/transparency/farcaster-manifest-rekor-receipt.json
git commit -m "record Farcaster manifest transparency receipt"
git push
```

## Verification flow

A third party can verify the chain by checking:

```text
manifest.json canonicalizes to manifest.jcs
manifest.jcs hashes to manifest.lock.json sha256
manifest.lock.json sha256 matches logged Rekor artifact
Rekor inclusion proof verifies against the transparency log
```

## What this proves

This proves:

- the lock hash existed at or before the Rekor integrated time
- the hash is publicly auditable
- later silent rewrites are detectable

This does not prove:

- the manifest is truthful
- the developer is authoritative
- the app is safe forever
- future versions are valid without their own verification

## Doctrine

Transparency is evidence, not authority.

```text
No receipt = no claim
No replay = no trust
authority=false
```
