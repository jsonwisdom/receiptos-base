# Lattice Batch Merkle Catalog

Issue: #37

## Use case

First cross-report use case: batch verification.

The batch Merkle catalog aggregates accepted report hashes into one root.

It does not add timeline order, relationship semantics, scoring, clustering, simulation, graph mutation, authority, or truth.

## Composition

```text
Flat hash catalogs -> Batch Merkle catalog
```

## Rules

- Input catalogs must be accepted flat hash maps.
- Leaves are `source_report_hash` keys.
- Leaves are deduplicated and sorted lexicographically.
- Binary tree.
- Single-leaf passthrough.
- Odd leaf count duplicates final leaf for the next level.
- Branch hash is `sha256(left_hex + right_hex)` as UTF-8 text.

## Command

```bash
python lattice/batch_merkle_catalog.py lattice/fixtures/rp-001-lattice-catalog.example.json lattice/fixtures/rp-002-eas-lattice-catalog.example.json
```

## Fixture

- `lattice/fixtures/rp-001-rp-002-batch-merkle.example.json`

## RP-001 + RP-002 root

```text
sha256:6ffc207fe8fb31296c27fc1457e233af771dca3800ce299cd262777fef790dad
```

## Boundary

The batch root commits to accepted report hashes only.

It does not inspect report bodies or infer meaning between reports.
