# Lattice Light Verifier Hook

Issue: #37

## Purpose

Standalone command for checking one report hash against a batch root.

It uses only:

- leaf hash
- sibling hash
- sibling position
- batch root

It does not load report bodies or catalogs.

## RP-002 EAS proof

```bash
python lattice/light_verify_inclusion.py \
  --leaf sha256:0ab9432b7988e016d3e7db76ca5e42e55705c173f987108ace4baad174fed8b1 \
  --sibling sha256:7107ad37be56fbd8872463c911d650d526f821c371986fd06dddf85378ecaaaa \
  --sibling-position right \
  --root sha256:6ffc207fe8fb31296c27fc1457e233af771dca3800ce299cd262777fef790dad
```

## RP-001 proof

```bash
python lattice/light_verify_inclusion.py \
  --leaf sha256:7107ad37be56fbd8872463c911d650d526f821c371986fd06dddf85378ecaaaa \
  --sibling sha256:0ab9432b7988e016d3e7db76ca5e42e55705c173f987108ace4baad174fed8b1 \
  --sibling-position left \
  --root sha256:6ffc207fe8fb31296c27fc1457e233af771dca3800ce299cd262777fef790dad
```

## Expected result

```json
{
  "light_verifier": true,
  "proof_valid": true,
  "authority": false,
  "truth_claim": false,
  "inference_performed": false,
  "state_mutated": false,
  "errors": []
}
```

## Boundary

The hook verifies inclusion only.

It does not add time order, relationships, scoring, simulation, graph mutation, authority, or truth.
