# JOY → receiptos-base Client Contract v0.1

## Purpose

This document defines the strict runtime seam between JOY and `receiptos-base`.

JOY is the runtime/client. `receiptos-base` is the Base-native receipt implementation rail. AL remains the governance/specification source.

## Boundary

JOY must not import AL internals.

JOY may consume only:

- `receiptos-base` public API contracts
- EAS schema and attestation constants exposed by `receiptos-base`
- replay result schema
- pinned doctrine/interface hashes

## Request Surface

`JOYReplayRequest` is the only admissible request shape for v0.1.

Required fields:

```text
requestId
subject
transformVersion
inputHash
replayMode
receiptIntent
authority
noFakeGreen
```

Required invariants:

```text
authority=false
noFakeGreen=true
transformVersion=v0.1.0
replayMode in [dry_run, witnessed_run]
```

## Response Surface

`ReceiptOSReplayResult` is the only admissible response shape for v0.1.

Required fields:

```text
requestId
status
stateRoot
receiptId
eventCount
authority
noFakeGreen
verifiedReplay
loadVerified
gateResult
```

Required invariants:

```text
authority=false
noFakeGreen=true
verifiedReplay=false unless promoted by verifier evidence
loadVerified=false unless a valid witness receipt exists
```

## Status Values

```text
ACCEPTED_FOR_REPLAY
WITNESS_ONLY
GOVERNANCE_GAP
REJECTED_CONTRACT_VIOLATION
```

## Non-Claims

This contract does not claim:

- LOAD_VERIFIED
- replay success
- wallet control
- Base endorsement
- truth authority

## Promotion Rule

A JOY response may not promote `verifiedReplay=true` or `loadVerified=true` from request content alone.

Promotion requires independent verifier evidence and a receipt witness satisfying the applicable schema.

## Current Classification

```text
contract_version: v0.1
classification: CLIENT_CONTRACT_ONLY
verifiedReplay: false
loadVerified: false
```
