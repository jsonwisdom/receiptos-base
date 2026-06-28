#!/usr/bin/env bash
set -e
for f in artifact-proofs/*.json; do
  python3 verify.py "$f" >/dev/null
done
echo "ROUND_016 standalone verifier PASS"
