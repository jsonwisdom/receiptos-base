# Lattice Merkle Catalog

Issue: #37

## Purpose

The Merkle catalog adds a commitment root over the flat hash map.

It does not add relations, scoring, clustering, simulation, graph mutation, authority, or truth.

## Composition

```text
Witness report -> Guard -> Admission gate -> Flat hash catalog -> Merkle catalog
```

## Initial target

- Binary tree
- Sorted leaves
- Single-leaf passthrough
- Odd leaf count duplicates the final leaf
- Branch hash: `sha256(left_hex + right_hex)` as UTF-8 text

## Commands

```bash
python lattice/merkle_catalog.py lattice/fixtures/rp-001-lattice-catalog.example.json
```

```bash
python lattice/merkle_catalog.py lattice/fixtures/rp-002-eas-lattice-catalog.example.json
```

## Fixtures

- `lattice/fixtures/rp-001-lattice-merkle.example.json`
- `lattice/fixtures/rp-002-eas-lattice-merkle.example.json`

## Boundary

The Merkle catalog commits to accepted report hashes only.

It does not inspect or reinterpret report contents.

## Next layer

A multi-leaf combined catalog can be added after this single-leaf invariant is stable.