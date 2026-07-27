#!/usr/bin/env bash
# Deterministic ARC/manifest.json audit primitive (Phase 1).
# Zero network. No timestamps in hash input. Dual provenance.
# Canonicalization contract: jq-sort-compact v1.0
set -euo pipefail

ARTIFACT="ARC/manifest.json"
MODE="working-tree"
COMMIT=""

usage() {
  cat <<'EOF'
Usage:
  ./scripts/arc-audit.sh          audit working tree
  ./scripts/arc-audit.sh COMMIT   audit pinned commit
EOF
  exit 1
}

if [[ $# -eq 1 ]]; then
  COMMIT="$1"
  MODE="commit"
elif [[ $# -gt 1 ]]; then
  usage
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

if [[ "$MODE" == "commit" ]]; then
  git cat-file -e "${COMMIT}^{commit}"
  git cat-file -e "${COMMIT}:${ARTIFACT}"
  git show "${COMMIT}:${ARTIFACT}" > "$TMPDIR/raw.json"
  GIT_BLOB_SHA1="$(git rev-parse "${COMMIT}:${ARTIFACT}")"
  REPO="$(basename "$(git rev-parse --show-toplevel)")"
  COMMIT="$(git rev-parse "${COMMIT}^{commit}")"
else
  if [[ ! -f "$ARTIFACT" ]]; then
    echo "error: $ARTIFACT not found in working tree" >&2
    exit 1
  fi

  cp "$ARTIFACT" "$TMPDIR/raw.json"
  GIT_BLOB_SHA1="$(git hash-object "$ARTIFACT")"
  REPO="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
  COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'uncommitted')"
fi

jq -S -c . "$TMPDIR/raw.json" > "$TMPDIR/canonical-line.json"
CANONICAL="$(cat "$TMPDIR/canonical-line.json")"
printf '%s' "$CANONICAL" > "$TMPDIR/canonical.json"

if command -v sha256sum >/dev/null 2>&1; then
  SHA256="$(sha256sum "$TMPDIR/canonical.json" | awk '{print $1}')"
else
  SHA256="$(openssl dgst -sha256 -r "$TMPDIR/canonical.json" | awk '{print $1}')"
fi

cat <<EOF
{
  "receipt_schema": "arc-audit-receipt",
  "receipt_version": "1.0",
  "repository": "$REPO",
  "mode": "$MODE",
  "commit": "$COMMIT",
  "artifact": "$ARTIFACT",
  "canonicalization": {
    "algorithm": "jq-sort-compact",
    "version": "1.0",
    "command": "jq -S -c ."
  },
  "hash_algorithm": "SHA-256",
  "sha256_canonical": "$SHA256",
  "git_blob_sha1": "$GIT_BLOB_SHA1",
  "status": "PASS"
}
EOF
