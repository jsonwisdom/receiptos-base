# Lattice Batch Root Manifest

Issue: #37

## First proof consumer

Light verifier.

It verifies one report hash against a batch root using sibling data. It does not load the full report body.

## Batch root

```text
sha256:6ffc207fe8fb31296c27fc1457e233af771dca3800ce299cd262777fef790dad
```

## Leaves

| report | leaf |
|---|---|
| RP-002 EAS | `sha256:0ab9432b7988e016d3e7db76ca5e42e55705c173f987108ace4baad174fed8b1` |
| RP-001 | `sha256:7107ad37be56fbd8872463c911d650d526f821c371986fd06dddf85378ecaaaa` |

Leaves are sorted lexicographically before root construction.

## Inclusion data

| target | sibling position | sibling |
|---|---|---|
| RP-002 EAS | right | `sha256:7107ad37be56fbd8872463c911d650d526f821c371986fd06dddf85378ecaaaa` |
| RP-001 | left | `sha256:0ab9432b7988e016d3e7db76ca5e42e55705c173f987108ace4baad174fed8b1` |

## Build command

```bash
python lattice/batch_root_manifest.py build lattice/fixtures/rp-001-lattice-catalog.example.json lattice/fixtures/rp-002-eas-lattice-catalog.example.json
```

## Manifest fixture

```text
lattice/fixtures/batch-root-manifest-rp001-rp002.example.json
```

## Boundary

The manifest and light verifier operate on hashes only.

No timeline ordering, relation claim, scoring, clustering, simulation, graph mutation, authority, or truth is added.
