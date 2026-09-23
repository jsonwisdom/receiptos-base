# Canonicalization Conformance v0.2.2 — Quarantine

**Status:** `QUARANTINED_DRAFT`  
**Authority:** `FALSE`  
**Promotion:** `PROHIBITED`  
**Audit gate:** `410 OPEN`

This directory contains fixture-only conformance work for the two locked profiles:

- `JAYWISDOM_NFC_RECEIPT_V1`
- `JAYWISDOM_BYTE_STRICT_EVIDENCE_V1`

It creates no serializer and changes no live rail.

```text
v0.2.2-quarantine/
├── corpus/       corrected authorized fixtures only
├── python/       live-Python-rail replay
├── typescript/   independent harness, added only after Python replay
└── results/      non-promoting replay outputs
```

## Locked execution order

```text
DIRECTORIES
→ CORRECTED CORPUS
→ PYTHON LIVE-RAIL REPLAY
→ TYPESCRIPT HARNESS
```

No result in this directory closes Audit #410, promotes a profile, mutates historical hashes, or activates signing or production authority.
