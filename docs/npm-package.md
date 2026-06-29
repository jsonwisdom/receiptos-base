# NPM Package Runbook

Package name:

```text
@jsonwisdom/farcaster-verify
```

Purpose:

```text
Authority=false Farcaster Mini App manifest verification.
```

## Commands exported

```bash
farcaster-verify-semantic
farcaster-verify-lock
farcaster-verify-rfc8785
farcaster-verify-invalid
farcaster-verify-fuzz
```

## Local verification

Before publishing:

```bash
npm install
npm run verify:farcaster
```

The `prepublishOnly` hook also runs the verifier before publish.

## Publish flow

```bash
npm login
npm publish --access public
```

## Consumer usage

```bash
npm install -D @jsonwisdom/farcaster-verify
npx farcaster-verify-rfc8785
npx farcaster-verify-invalid
npx farcaster-verify-fuzz
npx farcaster-verify-semantic
npx farcaster-verify-lock
```

## Environment overrides

```bash
MANIFEST_PATH=.well-known/farcaster/manifest.json \
MANIFEST_JCS_PATH=.well-known/farcaster/manifest.jcs \
MANIFEST_LOCK_PATH=.well-known/farcaster/manifest.lock.json \
npx farcaster-verify-semantic
```

## Doctrine

```text
authority=false
RFC8785 canonicalization
Replay First. Verify Everything.
```
