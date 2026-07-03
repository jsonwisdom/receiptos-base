# ReceiptOS Wire Workflow

Workflow file:

```text
.github/workflows/receiptos-wire.yml
```

Purpose:

- Install dependencies.
- Build the Next app.
- Run the fail-closed identity matrix.
- Run the production identity verifier.
- Optionally smoke-test deployed `/sign` and `/stream`.
- Upload verifier and stream artifacts.

## Modes

### PR / push

Runs automatically on pull requests and pushes to `main`.

Live ERC-1271 verification is non-blocking unless required manually.

### Manual dispatch

Inputs:

```text
deploy_url
require_live_signature
```

Default deploy URL:

```text
https://receiptos-frame-mvp.vercel.app
```

Set `require_live_signature=true` to make `SIGNATURE_VERIFIED` mandatory.

## Secret

For ERC-1271 smart-wallet verification, set this repository secret:

```text
BASE_RPC_URL
```

No private keys are needed.

## Boundary

This workflow verifies receipt wiring and identity binding only.

It preserves:

```json
{
  "verdict": "WITNESS_ONLY",
  "authority": false,
  "truth_claim": false
}
```
