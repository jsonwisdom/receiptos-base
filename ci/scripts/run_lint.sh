#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' 'ReceiptOS validator preflight: Python syntax and importability'
python -m compileall -q ep receiptos tests
python - <<'PY'
from ep.canonical import canonicalize
from receiptos.core.hash import canonical_json

assert canonicalize({"b": 2, "a": 1}).text == '{"a":1,"b":2}'
assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'
print('validator preflight: PASS')
PY
