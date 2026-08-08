# Agent Economics V0.1 Schema Pin

Status: ACTIVE / FAIL-CLOSED  
Authority: FALSE  
No Fake Green: TRUE

## Source

- Repository: `jsonwisdom/AL`
- Branch: `agent/jaywisdom-agent-economics-v0-1`
- Source commit: `af63889a692890cfd0e3ed74224b4feb1b614ac4`

The four files in this directory are vendored exact-byte copies of the AL truth-contract package.

## Pin Algorithm

The 40-hex identifiers reported by GitHub are **Git blob object IDs**. They are not plain `SHA1(file_bytes)`.

For file bytes `B`, the pinned value is:

```text
SHA1("blob " + decimal_byte_length(B) + NUL + B)
```

`economics.v0_1.schema_pin.verify_schema_pin()` recomputes that Git blob ID for every vendored file. It also reports ordinary SHA-256 of the bytes as diagnostic output, but the canonical cross-repository pin for V0.1 is the Git blob ID observed from AL.

## Pinned Blobs

```text
JAYWISDOM_AGENT_ECONOMICS_V0_1.schema.json
4ac089aa4824820634665f78a59b70e709c87292

ECONOMIC_DECISION_RECEIPT_V0_1.schema.json
0cf20aebc909b2f311868efdcf872b0f53af47ee

REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1.schema.json
bedfcca08ea9c4aa73ca2f68510a65dd58cb5ad2

JAYWISDOM_AGENT_ECONOMIC_GATE_V0_1.md
ecd02c3b5f299c506b7638ef68f6b92b4f7a1b01
```

## Import Boundary

`economics.v0_1.__init__` runs the pin verifier at import time.

```text
MISSING VENDORED FILE -> FAIL
BYTE DRIFT            -> FAIL
ALL FOUR MATCH        -> IMPORT MAY CONTINUE
```

A successful pin proves only byte equality with the pinned AL artifacts. It does not prove economic correctness, execution authority, payment, settlement, or profitability.
