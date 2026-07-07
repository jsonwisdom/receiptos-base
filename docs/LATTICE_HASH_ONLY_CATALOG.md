# Lattice Hash-Only Catalog

Issue: #37

## Purpose

The hash-only catalog is the next safe consumer after the lattice admission gate.

It records accepted ingestion artifacts in a flat map keyed by `source_report_hash`.

## Surface

```text
Witness report -> Serialization Guard -> Lattice admission -> Flat hash catalog
```

## Command

```bash
python lattice/catalog_accepted_report.py lattice/fixtures/rp-001-lattice-ingest.example.json
```

```bash
python lattice/catalog_accepted_report.py lattice/fixtures/rp-002-eas-lattice-ingest.example.json
```

## Output fixtures

- `lattice/fixtures/rp-001-lattice-catalog.example.json`
- `lattice/fixtures/rp-002-eas-lattice-catalog.example.json`

## Boundary

The catalog stores only:

- report hash
- source artifact path
- source report path
- guard status flags
- sticky false fields

It does not add scoring, clustering, simulation, meaning, or graph mutation.

## Next surface

After the flat map is stable, a Merkle catalog can be added as a separate layer.