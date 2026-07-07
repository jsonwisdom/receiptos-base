#!/usr/bin/env bash
set -euo pipefail

# One-shot EXT-001 mutator
# Usage: ./ztvs/mutate_ext001.sh <lane> <sha256_hash>
# Example: ./ztvs/mutate_ext001.sh PRC-JRN-EXT-001 22b00da...

LANE="${1:-}"
SHA="${2:-}"

if [[ -z "$LANE" || -z "$SHA" ]]; then
  echo "Usage: $0 <lane> <sha256_hash>" >&2
  exit 1
fi

if [[ ! "$SHA" =~ ^[0-9a-f]{64}$ ]]; then
  echo "FAIL: sha256_hash must be 64 lowercase hex characters" >&2
  exit 1
fi

ACTIVE_LANES="ACTIVE_LANES.md"
VALIDATOR="ztvs/active_lanes_validator.py"
MUTATOR="ztvs/ext001_mutator.py"

if [[ ! -f "$ACTIVE_LANES" ]]; then
  echo "FAIL: $ACTIVE_LANES not found" >&2
  exit 1
fi

if [[ ! -f "$VALIDATOR" ]]; then
  echo "FAIL: $VALIDATOR not found" >&2
  exit 1
fi

if [[ ! -f "$MUTATOR" ]]; then
  echo "FAIL: $MUTATOR not found. See ztvs/EXT001_MUTATION_RULES.md for manual-review mutation path." >&2
  exit 1
fi

# Pre-mutation validator
echo "Running pre-mutation validator..."
python3 "$VALIDATOR"

# Build EXT-001 payload
PAYLOAD=$(cat <<EOF
{"lane": "$LANE", "receipt_sha256": "$SHA"}
EOF
)

echo "Applying EXT-001 mutation for lane=$LANE sha256=$SHA..."
printf '%s\n' "$PAYLOAD" | python3 "$MUTATOR"

# Post-mutation validator
echo "Running post-mutation validator..."
python3 "$VALIDATOR"

echo "Mutation + validation complete. READY: ledger updated under authority=false."
