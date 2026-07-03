# AR-006: ReceiptOS Agent Receipt v0.2 EAS Schema

> Status: draft schema documentation for Base EAS registration
>
> Source anchor: `mvp-vertical-slice-complete`

This schema defines a lightweight EAS provenance index for ReceiptOS Agent Receipt v0.2 artifacts.

EAS is used as an index, not as the receipt database. Full receipt JSON, inputs, outputs, captured context, and policy details remain off-chain in the receipt artifact bundle. The on-chain attestation stores stable identifiers and verification state only.

## Schema String

```text
string receipt_version,string receipt_id,string content_hash,string policy_hash,string policy_id,string policy_version,string parent_hash,string manifest_hash,string terminal_state,bool policy_pass,bool authority,bool truth_claim,string agent_id,string action_type,string signature_scheme,string signature_public_key,string receipt_json_sha256,string verifier_version
```

## Field Reference

| Field | Type | Purpose |
|---|---|---|
| `receipt_version` | `string` | ReceiptOS protocol version, e.g. `agent-receipt/v0.2`. |
| `receipt_id` | `string` | Equal to `content_hash`; stable receipt identity. |
| `content_hash` | `string` | JCS SHA-256 over `inputs`, `outputs`, `captured_context`, `policy_hash`, `manifest_hash`, and `parent_hash`. |
| `policy_hash` | `string` | Hash of the policy material used by the verifier. Current policy hash material is `{ version: policy.policy_version, rules: policy.rules || [] }`. |
| `policy_id` | `string` | Identifier for the policy used to evaluate the receipt. |
| `policy_version` | `string` | Version string recorded from the policy object. |
| `parent_hash` | `string` | Prior receipt `content_hash`, or a null-equivalent string for genesis. It is not an EAS UID. |
| `manifest_hash` | `string` | Hash of the referenced off-chain artifact manifest. Manifest completeness is self-attested. |
| `terminal_state` | `string` | One of `VERIFIED`, `STALE`, `REJECTED`, or `MISMATCHED` for the current vertical slice. |
| `policy_pass` | `bool` | Result of the policy check. A policy-denied receipt may still be signed evidence. |
| `authority` | `bool` | Must be `false`. Evidence flag only; not an authority claim. |
| `truth_claim` | `bool` | Must be `false`. The attestation is provenance, not objective truth. |
| `agent_id` | `string` | Identifier of the producing agent. |
| `action_type` | `string` | Category of the recorded operation, e.g. `tool_call` or `llm_call`. |
| `signature_scheme` | `string` | Current MVP: `ed25519`. |
| `signature_public_key` | `string` | Public key used to verify the receipt signature. |
| `receipt_json_sha256` | `string` | SHA-256 of the full off-chain receipt JSON artifact. |
| `verifier_version` | `string` | Version of the verifier logic used to produce the terminal state. |

## Content Hash Rule

The tagged v0.2 receipt specification defines `content_hash` over:

```text
inputs + outputs + captured_context + policy.policy_hash + manifest_hash + parent_hash
```

The EAS attestation does not store those full objects. It stores the resulting `content_hash` and `receipt_json_sha256`, allowing off-chain resolution and verification of the full receipt bundle.

## Policy Hash Rule

The tagged demo computes policy hash material from:

```js
{
  version: policy.policy_version,
  rules: policy.rules || []
}
```

This avoids storing `policy_hash` inside the policy file itself and prevents circular hashing.

## Terminal-State Semantics

| Terminal | Meaning |
|---|---|
| `VERIFIED` | Signature, policy hash, and replay all match. |
| `STALE` | Signature is valid, but current policy hash differs from recorded policy hash. |
| `REJECTED` | Receipt is malformed, authority boundary is violated, or signature is invalid. |
| `MISMATCHED` | Signature is valid, but replayed `content_hash` diverges from recorded `content_hash`. |

Verification order:

```text
parse / authority -> signature -> policy_hash freshness -> content_hash replay
```

## Operational Invariants

1. `authority` must be `false`.
2. `truth_claim` must be `false`.
3. `receipt_id` must equal `content_hash`.
4. `parent_hash` must refer to the prior receipt `content_hash`, not an EAS UID.
5. `signature_scheme` must match the receipt signature implementation. Current MVP uses `ed25519`.
6. EAS is a provenance index, not a full receipt database.
7. The attestation must not claim semantic correctness, legal truth, external dependency honesty, policy quality, or manifest completeness.

## Suggested Attestation Meaning

```text
This attestation records that a ReceiptOS Agent Receipt v0.2 artifact exists,
has the listed hashes and terminal state, and was verified under authority=false
and truth_claim=false. It does not assert semantic truth, legal truth, external
dependency honesty, manifest completeness, or policy quality.
```

## Registration Notes

Before registering on Base EAS, verify the current Base SchemaRegistry address against official EAS documentation or the EAS app transaction path.

Use a zero-address resolver only if no custom resolver behavior is required.
