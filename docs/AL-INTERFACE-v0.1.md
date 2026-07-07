# AL → receiptos-base Interface v0.1

## Purpose

This document defines the only admissible interface between AL governance/doctrine artifacts and `receiptos-base` implementation artifacts.

`AL` remains the specification and governance source. `receiptos-base` implements Base-native receipt infrastructure.

## Boundary

Clients must not import AL internals directly. They consume only:

- EAS schema UIDs from `eas/`
- the public API surface
- the replay result schema
- pinned doctrine snapshots or attestations

## Governance → receiptos-base

AL governance proposals that affect receipt semantics must be translated into:

- updated EAS schemas in `eas/schemas/`
- migration attestations, bootstrap attestations, or upgrade attestations
- verifier test fixtures

Breaking changes require a new schema UID and a compatibility note.

## Doctrine → receiptos-base

Doctrine is enforced through type-level invariants and verifier checks.

Required invariants:

```text
authority=false
no_fake_green=true
replay_deterministic=true
schema_version_pinned=true
```

## Replay Theory → `replay/`

Replay must be deterministic, auditable, and hash-producing. Replay output is not narrative authority.

Required output:

- `stateRoot`
- `eventCount`
- `strategy`
- `authority=false`
- `noFakeGreen=true`
- `verifiedReplay=false` unless a verifier explicitly promotes it from evidence

## Versioning Rule

Any change to this interface bumps the minor version and requires a bootstrap or migration attestation referencing the new interface hash.

## Current Classification

```text
interface_version: v0.1
classification: BOOTSTRAP_INTERFACE
load_verified: false
verified_replay: false
```
