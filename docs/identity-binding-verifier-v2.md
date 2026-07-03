# Identity Binding Verifier v2

Status: EIP191_OR_ERC1271_VERIFICATION_PENDING

## Purpose

ReceiptOS identity binding now supports two wallet paths:

1. Externally owned account signatures using EIP-191 / `personal_sign`.
2. Smart wallet signatures using ERC-1271 `isValidSignature(bytes32,bytes)`.

The target identity is:

```text
jaywisdom.base.eth
0xA380552a27b0a5a2874Ea7AA52CAC09f542002E8
```

## Boundary

Signature verification proves identity binding only.

It does not create truth authority.

All verifier outputs preserve:

```json
{
  "verdict": "WITNESS_ONLY",
  "authority": false,
  "truth_claim": false
}
```

## Files

```text
provenance/identity-binding/jaywisdom-identity-binding.txt
provenance/identity-binding/jaywisdom-identity-binding.sig
SHA256SUMS
```

`SHA256SUMS` must include both exact paths.

## Verifier paths

### EIP-191

For normal 65-byte signatures:

```js
verifyMessage(bindingText, signature)
```

The recovered address must equal:

```text
0xa380552a27b0a5a2874ea7aa52cac09f542002e8
```

### ERC-1271

For smart-wallet signatures:

```solidity
isValidSignature(bytes32 hash, bytes signature) returns (bytes4)
```

Expected magic value:

```text
0x1626ba7e
```

The hash is the EIP-191 digest of the exact identity-binding text.

## Runtime environment

ERC-1271 requires an RPC endpoint:

```text
BASE_RPC_URL
```

Fallbacks:

```text
ETH_RPC_URL
RPC_URL
```

If no RPC is configured, the verifier fails closed:

```text
PENDING_SIGNATURE / WITNESS_ONLY / authority=false / truth_claim=false
```

## Current state

- A380 signature payload captured.
- Dual-path verifier committed.
- `/stream` endpoint committed.
- SHA256SUMS committed.
- Full SIGNATURE_VERIFIED promotion waits for live ERC-1271 check with RPC configured.
