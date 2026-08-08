# Agent Economics V0.1 Schema Pin

Status: ACTIVE / FAIL-CLOSED  
Authority: FALSE  
No Fake Green: TRUE

## Source

- Repository: `jsonwisdom/AL`
- Branch: `agent/jaywisdom-agent-economics-v0-1`
- Source commit: `af63889a692890cfd0e3ed74224b4feb1b614ac4`

The four files in this directory are vendored exact-byte copies of the AL truth-contract package.

## Pin Algorithms

The 40-hex identifiers reported by GitHub are **Git blob object IDs**. They are not plain `SHA1(file_bytes)`.

For file bytes `B`, the Git blob ID is:

```text
SHA1("blob " + decimal_byte_length(B) + NUL + B)
```

V0.1 also pins ordinary SHA-256 of the exact file bytes. `verify_schema_pin()` requires both digests to match.

## Pinned Bytes

```text
JAYWISDOM_AGENT_ECONOMICS_V0_1.schema.json
  git_blob_sha1 = 4ac089aa4824820634665f78a59b70e709c87292
  sha256        = dbd0c30a1e916b0cce53f5ca102d0274d6438437cd163b00dca321b25de0c171

ECONOMIC_DECISION_RECEIPT_V0_1.schema.json
  git_blob_sha1 = 0cf20aebc909b2f311868efdcf872b0f53af47ee
  sha256        = e85f4a806be8d25bcc48a290061b3a770ff708ffe3bd04f74f03589f27fa32a1

REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1.schema.json
  git_blob_sha1 = bedfcca08ea9c4aa73ca2f68510a65dd58cb5ad2
  sha256        = 179df010c0ec1b657f1ea60b6d2265c2c83ef8f40fd88b6822a741794e77468a

JAYWISDOM_AGENT_ECONOMIC_GATE_V0_1.md
  git_blob_sha1 = ecd02c3b5f299c506b7638ef68f6b92b4f7a1b01
  sha256        = 8922866e176ad55f26c0045d4e3638cb69863fc81c737512f2ffaf9292baf5ba
```

## Import Boundary

`economics.v0_1.__init__` runs the pin verifier at import time.

```text
MISSING VENDORED FILE -> FAIL
GIT BLOB DRIFT       -> FAIL
SHA-256 DRIFT        -> FAIL
ALL FOUR MATCH       -> IMPORT MAY CONTINUE
```

A successful pin proves only byte equality with the pinned AL artifacts. It does not prove economic correctness, execution authority, payment, settlement, or profitability.
