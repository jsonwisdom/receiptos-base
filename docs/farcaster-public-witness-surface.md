# Farcaster Public Witness Surface

## Purpose

This document records the public Farcaster witness surface for the locked JAYWISDOM manifest.

```text
public_witness_url: https://farcaster.xyz/cmptrwsdm
manifest_id: jaywisdom
manifest_path: .well-known/farcaster/manifest.json
canonical_manifest_path: .well-known/farcaster/manifest.jcs
lock_path: .well-known/farcaster/manifest.lock.json
lock_sha256: d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce
authority: false
truth_claim: false
```

## Boundary

The Farcaster profile page is a public witness surface, not the canonical ledger.

It may be used by external observers to inspect social identity continuity, cast history, and public profile presence. It must not be treated as an authoritative source of truth for the manifest, the domain, or any underlying claim.

The canonical replay path remains:

```text
.well-known/farcaster/manifest.json
  -> RFC8785 canonicalization
  -> .well-known/farcaster/manifest.jcs
  -> SHA-256
  -> .well-known/farcaster/manifest.lock.json
```

GREEN means the receipt verified, the hash matched, replay succeeded, and authority remained false.

GREEN does not mean the underlying claim is true.

## Witness Role

```json
{
  "witness_surface": "https://farcaster.xyz/cmptrwsdm",
  "role": "public_identity_projection",
  "canonical_manifest": false,
  "source_of_truth": false,
  "replay_surface": true,
  "authority": false,
  "truth_claim": false
}
```

## Invariant

Public profile presence is evidence of observable surface continuity only. It does not mutate the locked manifest, elevate authority, or resolve truth claims.

Timestamp, not tribunal.
