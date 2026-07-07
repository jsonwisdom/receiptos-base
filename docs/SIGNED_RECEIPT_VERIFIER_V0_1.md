# Signed Receipt + Transparency Verifier v0.1

## Purpose

This verifier is independent from the load runner. Runner output alone cannot promote a witness.

## Inputs

```text
receipt witness JSON
transparency log JSON
chain head JSON
LOAD_VERIFICATION_WITNESS_V0_1 schema
```

## Checks

```text
receipt_digest_match
signature_valid
hash_chain_continuous
doctrine_guards_pass
failed_conditions_empty
```

## Output

```text
SIGNED_LOAD_RECEIPT_VERIFIER_V0_1
status = LOAD_VERIFIED | GOVERNANCE_GAP
canonical_digest
authority=false
no_fake_green=true
```

## Promotion rule

`LOAD_VERIFIED` is emitted only when all verifier checks pass and the witness itself claims `gate_result.status = LOAD_VERIFIED`.

Otherwise the verifier emits `GOVERNANCE_GAP`.

## Ed25519 signature requirement

A `LOAD_VERIFIED` witness must include a schema-valid `signature` object:

```text
alg = Ed25519
public_key = 32-byte hex public key
signature = 64-byte hex signature
```

The verifier checks the signature over the canonical witness payload with the `signature` field removed.

A missing, malformed, invalid, or tampered signature fails closed to `GOVERNANCE_GAP`.
