# Meme Court Frame

MVP Frame endpoint for the ReceiptOS Meme Court / Court Game vertical slice.

Doctrine:

> No receipt = no authority.

## Live endpoint contract

When deployed, the stable route is:

```text
/api/frame
```

Both `GET` and `POST` return the same MVP evidence payload.

## Current terminal state

```text
PENDING_SIGNATURE
```

This is intentional. The known EAS attestation exists as an on-chain statement-hash witness, but the wallet signature bundle has not yet been committed.

## Known evidence

- EAS Schema: `#1648`
- Schema UID: `0x45af9479e460c501c71e09679936d9dc20eb3a37f0cc0586d8d6937d9e1ec80d`
- Attestation UID: `0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6`
- Repository: `jsonwisdom/receiptos-base`
- Commit: `2c7b4aa384265596a2c55df7b877e6874896573b`
- Statement SHA-256: `6928aeed37e3d86cf1952a42dfc82b2de214b347284c62a24534baf036e03c5e`
- authority: `false`
- truth_claim: `false`

## Next required evidence

- `provenance/identity-binding/jaywisdom-identity-binding.sig`
- `provenance/identity-binding/SHA256SUMS`

Until those are committed and verified, this frame must not return `VERIFIED` for the known UID.

## Scope boundary

This endpoint does not assert legal identity, copyright ownership, authorship, or external truth. It only reports the current verification state of the Meme Court receipt flow.
