# Identity Binding Verifier v2 Status

Commits added for GitFix dual-path verification:

- `eb0db17b15134bcbeb85787616473c2193ef0531` — `scripts/verify-identity-binding.mjs` dual path: EIP-191 for EOAs, ERC-1271 for smart wallets.
- `8ef755703f5d7b64a8c87762bf047a58025c9adf` — fixture matrix adapted for dual-path verifier.
- `75e70737c2e657f093ed8992273e2dd643fefc64` — `/stream` endpoint with deterministic JSON and ETag.
- `96f5a4519d836bda769586c3e5aca89f501e8c8e` — identity binding text.
- `005884ebd87afe07698bc574b1ec88730c9af3f2` — A380 smart-wallet signature payload.
- `3ad6a0227d2ae5a6e29ac65fa15a3678afba8541` — SHA256SUMS for identity binding files.

Boundary:

- Signature verification proves identity binding only.
- `authority=false` and `truth_claim=false` remain invariant.
- No private keys.
- No transaction signing.
- ERC-1271 verification requires `BASE_RPC_URL` or compatible RPC env.

Current state:

```text
A380_SIGNATURE_CAPTURED
EIP191_OR_ERC1271_VERIFICATION_PENDING
```

Promotion to `SIGNATURE_VERIFIED` requires a live ERC-1271 `isValidSignature` pass with magic value `0x1626ba7e`.
