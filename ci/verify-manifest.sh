#!/usr/bin/env bash
# verify-manifest.sh — Verify cryptographic integrity of a frozen conformance bundle.
# If no manifest.json exists yet, reports SKIP (not FAIL).
# Infrastructure only. No protocol semantics.
set -euo pipefail

BUNDLE_ROOT="${1:-conformance/v1.0}"
MANIFEST="$BUNDLE_ROOT/manifest.json"
SHA256SUMS="$BUNDLE_ROOT/SHA256SUMS"

if [[ ! -f "$MANIFEST" && ! -f "$SHA256SUMS" ]]; then
  echo "SKIP: no frozen manifest or SHA256SUMS found at $BUNDLE_ROOT"
  echo "This is expected until PR-5 publishes the first frozen bundle."
  exit 0
fi

FAIL=0

if [[ -f "$SHA256SUMS" ]]; then
  echo "Verifying SHA256SUMS..."
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$BUNDLE_ROOT" && sha256sum -c SHA256SUMS) || FAIL=1
  elif command -v shasum >/dev/null 2>&1; then
    # macOS fallback
    while read -r hash file; do
      actual=$(shasum -a 256 "$BUNDLE_ROOT/$file" | awk '{print $1}')
      if [[ "$actual" != "$hash" ]]; then
        echo "FAIL: $file expected $hash got $actual"
        FAIL=1
      else
        echo "OK: $file"
      fi
    done < "$SHA256SUMS"
  else
    echo "WARN: no sha256sum/shasum available; cannot verify checksums"
  fi
fi

if [[ -f "$MANIFEST" ]]; then
  echo "Manifest present: $MANIFEST"
  # Basic structural check only — full semantic validation belongs to the implementation under test.
  if command -v jq >/dev/null 2>&1; then
    jq -e . "$MANIFEST" >/dev/null || { echo "FAIL: manifest.json is not valid JSON"; FAIL=1; }
  else
    echo "WARN: jq not available; skipping JSON structural check"
  fi
fi

if [[ $FAIL -ne 0 ]]; then
  echo "Manifest verification FAILED"
  exit 1
fi

echo "Manifest verification PASSED (or SKIPPED)"
exit 0
