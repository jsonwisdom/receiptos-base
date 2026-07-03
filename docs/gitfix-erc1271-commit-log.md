# GitFix ERC-1271 Patch Set

Docket: `jsonwisdom/receiptos-base#57`

## Patch commits

- `eb0db17b15134bcbeb85787616473c2193ef0531` — dual-path verifier in `scripts/verify-identity-binding.mjs`.
- `8ef755703f5d7b64a8c87762bf047a58025c9adf` — dual-path fixture matrix support.
- `75e70737c2e657f093ed8992273e2dd643fefc64` — `/stream` route with deterministic JSON + ETag.
- `96f5a4519d836bda769586c3e5aca89f501e8c8e` — identity-binding text.
- `005884ebd87afe07698bc574b1ec88730c9af3f2` — A380 smart-wallet signature payload.
- `3ad6a0227d2ae5a6e29ac65fa15a3678afba8541` — root `SHA256SUMS`.
- `b949ba3ef319ea6f2e9302d3a7f1da7fbce4ae2a` — verifier v2 docs.
- `889c94e0defc672fd4924e8faf6fdb6b60fcbb4a` — verifier v2 status log.
- `d4c7276cdc61af9f6726c379731099116511ae8f` — ROS-0006 Authorized Identity invariant.
- `c2efcf64cf7d37a8731e34b5d1023254a679168f` — Docket #57 binding to ROS-0006.
- `3e79dd803057e73387f1076e3d656dfef1f2db35` — ReceiptOS Wire workflow bound to ROS-0006.

## Verification logic

Normal EOA signatures:

```text
ethers.verifyMessage(bindingText, signature)
```

Smart-wallet signatures:

```text
ERC-1271 isValidSignature(hashMessage(bindingText), signature)
```

Expected magic value:

```text
0x1626ba7e
```

## Runtime requirement

ERC-1271 requires one RPC env var:

```text
BASE_RPC_URL
```

Fallbacks:

```text
ETH_RPC_URL
RPC_URL
```

## Boundary

The verifier may report `SIGNATURE_VERIFIED`, but the verdict remains `WITNESS_ONLY` and both authority flags remain false.

```json
{
  "verdict": "WITNESS_ONLY",
  "authority": false,
  "truth_claim": false
}
```

## Current state

```text
RECEIPTOS_WIRE_WORKFLOW_SUCCESS
ROS-0006_ACTIVE
DOCKET_57_BOUND
```

ROS-0006 makes the Authorized Identity the invariant and assigns the canonical verification path by identity type: EIP-191 for EOAs and ERC-1271 for contract accounts.
