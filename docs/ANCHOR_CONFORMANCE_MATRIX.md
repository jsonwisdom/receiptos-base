# Anchor Conformance Matrix

Issue: #39

## Purpose

One command checks positive and negative storage-anchor behavior.

## Command

```bash
python audit/anchor_conformance_matrix.py --repo-root .
```

## Fixture

```text
audit/fixtures/anchor-conformance-matrix.example.json
```

## Cases

- positive storage-time anchor
- bad timestamp shape
- wrong anchor semantics
- unauthorized anchor field

## Expected result

```json
{
  "anchor_conformance_matrix": true,
  "matrix_passed": true,
  "case_count": 4,
  "positive_count": 1,
  "negative_count": 3,
  "authority": false,
  "truth_claim": false,
  "inference_performed": false,
  "state_mutated": false,
  "errors": []
}
```

## Boundary

Only storage-time anchors pass.

No timeline meaning is added.
