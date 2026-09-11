# CEG v1.0 Conformance Bundle Layout

**Status:** Structure only — no frozen artifacts published yet.

This directory defines the canonical layout for CEG v1.0 conformance bundles.

## Directory Structure

```
conformance/v1.0/
├── README.md                 # This file
├── ledger/                   # Canonical ObservationLedger artifacts
├── canonicalization/         # Expected canonicalization outputs
├── provenance/               # Expected provenance validation outputs
├── graph_integrity/          # Expected graph validation outputs
├── promotion/                # Expected promotion outputs
├── replay/                   # Expected replay report structure
└── final/                    # Expected final graph and explanations
```

## Frozen Artifacts

No frozen conformance bundle is present in this repository at the time of writing.

When the first release-candidate bundle is published (PR-5), the following files will appear:

- `manifest.json` — cryptographic inventory of every artifact
- `SHA256SUMS` — canonical checksum file
- Concrete JSON artifacts under each subdirectory

Until that time, the subdirectories remain empty (or contain only `.gitkeep` files) so that the layout is version-controlled and auditable.

## How to Use

1. Implementations under test consume a published frozen bundle.
2. They execute the replay procedure defined in `spec/CONFORMANCE.md`.
3. They produce a replay report that is compared against the published artifacts.

Placeholder or dummy hashes MUST NOT be committed. Only cryptographically honest artifacts generated from real evidence are allowed.

## Relation to the Specification

All behavioral requirements are defined in:

- `spec/EVIDENCE_GRAPH.md` — protocol semantics
- `spec/CONFORMANCE.md` — conformance and replay rules

This directory only holds the evidence against which those rules are tested.
