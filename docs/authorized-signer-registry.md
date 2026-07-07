# EXT-104 — Authorized Signer Registry

## Purpose

EXT-104 defines a replay-safe Authorized Signer Registry for the JAYWISDOM / ReceiptOS Frame stack.

The Frame must not know who the master signer is, why a key is authorized, or whether a key was revoked. It only reads the current registry state and verifies math against that state.

## Boundary

Signer diversity is a verification surface, not an authority surface.

```json
{
  "frame_mode": "EYES_NO_HANDS",
  "registry_status": "PENDING_REAL_SIGNER_REGISTRY",
  "authority": false,
  "truth_claim": false,
  "mutation": null,
  "mutations": []
}
```

## Registry Rule

```text
If signer_id is not present in authorized_signers[], it is unauthorized.
If signer_id is present, the Frame may verify a signature.
Membership alone does not make a signature valid.
A valid signature does not create truth authority.
```

## Source of Truth

The authorized signer set must be derived from a canonical registry artifact bound to the manifest lock state.

Until that artifact exists, the registry remains pending and empty.

The Frame must not cache active keys as policy. It may cache responses only as ordinary transport optimization if the canonical registry hash remains unchanged.

## Public Endpoints

```text
GET  /api/frame/authorized-signers
POST /api/frame/verify-signature
POST /api/frame/verify-multisig
```

## Verification Logic

```text
1. Read current authorized_signers[] from canonical registry state.
2. Confirm signer_id is present in authorized_signers[].
3. If absent, return UNAUTHORIZED_SIGNER.
4. If present, verify signature over message/payload hash.
5. Return valid=true or valid=false.
6. Do not explain policy reasons for membership.
7. Do not mutate registry.
8. Preserve authority=false and truth_claim=false.
```

## Revocation Model

There is no Frame-level revoke command.

Revocation is modeled as absence from the current canonical authorized_signers[] set.

The Frame only observes the set. It does not manage the set.

## Multisig Caveat

If the canonical registry defines a threshold, the Frame may verify whether the submitted signer set satisfies M-of-N. It may not choose the threshold itself.

## Forbidden Behavior

```text
authority=true
truth_claim=true
master_key assumption
registry mutation
signer addition by Frame
signer removal by Frame
policy explanation as source of truth
silent signer cache override
CRYPTOGREEN emission from membership alone
```

## Invariant

The Frame verifies signatures from a defined set. It does not govern the set.

Timestamp, not tribunal.
