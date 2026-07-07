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

## ROS-0006 Binding

ReceiptOS Wire is bound to:

```text
ROS-0006: Authorized Identity Invariant
```

The workflow verifies identity bindings against the operator's Authorized Identity.

The Authorized Identity MAY be:

- an EOA verified by EIP-191 `personal_sign`
- a contract account verified by ERC-1271 `isValidSignature`

The workflow MUST NOT force EIP-191 posture onto contract accounts.

Unknown identity types fail closed.

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

Suggested public Base RPC for initial verification:

```text
https://mainnet.base.org
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

## Canonical State

```text
ROS-0006_ACTIVE
RECEIPTOS_WIRE_WORKFLOW_SUCCESS
DOCKET_57_BOUND
```
