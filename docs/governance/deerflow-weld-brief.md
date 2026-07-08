# DeerFlow to ReceiptOS Weld Brief

Issue: #128  
Move: 2  
Base merge commit: `86550e7c461220847b5e2d48cc33012b51e23efb`

## Purpose

This brief defines the governed weld between an external execution harness and ReceiptOS.

DeerFlow may produce multi-step work outputs. ReceiptOS decides whether the resulting observation is admissible.

The weld does not grant DeerFlow authority. It accepts a bounded `cloud_observation` packet, validates it against the ReceiptOS read-only membrane, and returns either an admissible deterministic receipt surface or a deterministic rejection.

## Weld scope

The initial weld scope is intentionally narrow:

- external harness identity: `DeerFlow`
- payload type: `cloud_observation`
- validation surface: existing GCP read-only packet validator
- admissible outcome: deterministic PASS with output hash
- inadmissible outcome: fail-closed `WeldValidationError`

The weld validates observation packets that have already been produced by another system. It does not perform the observed work itself.

## Governance assertions

- `authority=false` is mandatory at the weld packet and cloud observation levels.
- `fake_green` is forbidden.
- a missing receipt anchor is inadmissible.
- non-read-only command claims are inadmissible.
- malformed command arrays are inadmissible.
- action authority cannot be inferred from an address, label, fixture, or receipt.
- output hashes must be deterministic over canonical JSON.

## Test coverage requirements

Move 2 cannot promote unless tests prove:

1. a truthful read-only DeerFlow observation validates;
2. the valid observation produces the expected deterministic output hash;
3. a non-read-only or lied observation fails closed;
4. the failure is surfaced through `WeldValidationError`;
5. the existing GCP read-only validator remains the command membrane.

## Rollback criteria

Rollback or block promotion if any of the following occur:

- `authority` is changed to `true` anywhere in the weld path;
- validation performs external work instead of validating an observation packet;
- a non-read-only command claim becomes admissible;
- a negative fixture passes;
- output hashes become non-deterministic;
- CI or deterministic verification fails;
- the PR attempts to close #128 without fixtures and tests.

## Boundary

This document does not authorize external execution, secrets handling, signing, or autonomous action authority.

Gate > stars.
