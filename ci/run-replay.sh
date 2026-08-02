#!/usr/bin/env bash
# run-replay.sh — Invoke independent replay against a frozen conformance bundle.
# If no frozen bundle exists, reports SKIP.
# Infrastructure only. No protocol semantics. Does not implement CEG rules.
set -euo pipefail

BUNDLE_ROOT="${1:-conformance/v1.0}"
REPLAY_CMD="${CEG_REPLAY_CMD:-}"

if [[ ! -f "$BUNDLE_ROOT/manifest.json" && ! -f "$BUNDLE_ROOT/SHA256SUMS" ]]; then
  echo "SKIP: no frozen conformance bundle present at $BUNDLE_ROOT"
  echo "Replay will be exercised once PR-5 publishes the first frozen artifacts."
  exit 0
fi

if [[ -z "$REPLAY_CMD" ]]; then
  echo "SKIP: CEG_REPLAY_CMD environment variable not set."
  echo "Set CEG_REPLAY_CMD to the command that performs independent replay"
  echo "(e.g. 'python -m ceg.replay --bundle $BUNDLE_ROOT')."
  exit 0
fi

echo "Running replay: $REPLAY_CMD"
eval "$REPLAY_CMD"
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
  echo "Replay FAILED with exit code $STATUS"
  exit $STATUS
fi

echo "Replay PASSED"
exit 0
