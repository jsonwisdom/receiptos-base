# ReceiptOS CLI Contract v0.1

## Purpose

Defines the behavioral CLI contract before implementation.

The CLI verifies structure, hashes, manifests, invariants, and replay outputs. It does not declare truth. Authority remains false.

## Command Surface

receiptos manifest verify <manifest.json>
receiptos tree hash <receipts.jsonl>
receiptos schema validate <receipt.json>
receiptos invariants check <run_dir>
receiptos replay run <manifest.json> --receipts <receipts.jsonl>
receiptos replay verify <run_dir>

## Exit Codes

0 PASS
1 USAGE_ERROR
2 INPUT_MISSING
3 SCHEMA_FAIL
4 TREE_HASH_FAIL
5 MANIFEST_FAIL
6 INVARIANT_FAIL
7 REPLAY_FAIL
8 NON_DETERMINISTIC
9 INTERNAL_ERROR

## Invariants

- Read-only by default
- Deterministic output
- No network dependency
- No mutation of source receipts
- No authority escalation
- authority:false required

## Next Layer

schemas/receipt.schema.json
