# Validation Log — Observation Protocol V1

Status: seeded from Issue #90 receipts.
Authority: false.

## Run 1 — Failed

Environment: sandbox without `jsonschema` available.

Result: certification refused because full JSON Schema validation could not run.

Meaning: useful failure receipt. Not eligible for tag.

## Run 2 — Pasted external receipt

Command:

```bash
python3 test_negative_fixtures.py
```

Output:

```text
PASS - positive packet passes
PASS - tampered raw payload fails
PASS - missing capture_id fails
PASS - authority:true fails
PASS - observed:false with value fails
PASS - capture notes field fails
PASS - empty referenced_capture_ids fails

7/7 checks passed.
CERTIFICATION PASSED. Eligible for validation log + tag.
Exit code: 0
```

Status: content certification receipt recorded.

## Run 3 — Required repo-local execution

After the files are populated in `jsonwisdom/receiptos-base`, run:

```bash
cd ~/receiptos-base
python3 tests/observation/test_negative_fixtures.py
echo "Exit code: $?"
```

Paste the exact output below before cutting `observation-protocol-v1`.

```text
PENDING
```

## Tag rule

Do not cut `observation-protocol-v1` until Run 3 is pasted with exit code `0` from the actual repository checkout.
