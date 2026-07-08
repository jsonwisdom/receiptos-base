# GPK Factory First Controlled Test Cycle

**Target:** `gpk-card-test-001`  
**Factory:** Jay's GitHub Garbage Pail Kids Factory  
**Status:** READY_TO_RUN  
**Authority:** false

## Signal Core

Factory tooling is isolated, witnessed, and invariants locked. Disposable card stub primes the goblin pipeline:

```text
Receipt Ricky -> Canon Carrie -> Lore Larry -> Press Patty
```

No real canon risk. Lineage + outbox flow is clean GitHub-native.

## Confirmed State

```text
AGENTS_DEFINED: true
CANON_MUTATION: false
REAL_CANON_TOUCHED: false
AUTHORITY: false
FIRST_TEST_TARGET: gpk-card-test-001
STATUS: AGENTS_DEFINED_NOT_YET_EXECUTED
```

## Execution Commands

```bash
cd ~/receiptos-base
git pull origin main
bash .github/workflows/gpk-lineage-check.sh main HEAD
python3 tools/run_gpk_factory_test.py
cat agents/gpk-factory/outbox/gpk-card-test-001/factory_test_summary.json
```

## Expected Witness Output

```text
Lineage check: PASS
GPK factory test: PASS
outbox=agents/gpk-factory/outbox/gpk-card-test-001
```

## Audit Targets

When `factory_test_summary.json` is returned, audit for:

- evidence pointers / commit hashes
- goblin output coherence
- quarantine invariants
- iteration deltas
- next card schema requirements
- Ollie activation readiness

## Boundary

```text
REAL_CANON_TOUCHED: false
QUARANTINE_TOUCHED: false
AUTHORITY: false
NO_SILENT_MUTATION: true
```

## Next Action

Run the sequence locally, in Cloud Shell, or in another trusted shell. Paste `factory_test_summary.json` plus lineage output back into the thread for audit, compression, and next-layer shipping.
