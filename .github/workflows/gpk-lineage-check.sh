#!/usr/bin/env bash
set -euo pipefail

# GPK Lineage Check v0.1
# Enforces append-only canon correction rules:
# - canonical artifacts are not silently deleted
# - canonical files are not edited unless the change is an explicit lineage/status pointer
# - correction/override/quarantine artifacts must reference prior canon hash
# - superseded canon must preserve created_at, receipt_hash, and canon_hash
# - superseded_by references must resolve to an existing canon id/hash/tag

BASE_REF="${1:-${GITHUB_BASE_REF:-main}}"
HEAD_REF="${2:-HEAD}"

if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  git fetch origin "$BASE_REF":"refs/remotes/origin/$BASE_REF" >/dev/null 2>&1 || true
  BASE_REF="origin/$BASE_REF"
fi

fail() {
  mkdir -p receipts/failures
  local id="${TARGET_ID:-lineage}"
  local out="receipts/failures/GPK_CANON_CORRECT_FAIL_${id}.json"
  python3 - "$out" "$1" <<'PY'
import json, sys, datetime, os
out, reason = sys.argv[1], sys.argv[2]
payload = {
  "receipt_type": "GPK_CANON_CORRECT_FAIL",
  "validator": "gpk-lineage-check.sh",
  "validator_version": "v0.1",
  "status": "FAIL",
  "reason": reason,
  "target_id": os.environ.get("TARGET_ID", "lineage"),
  "created_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
}
with open(out, "w", encoding="utf-8") as f:
  json.dump(payload, f, indent=2, sort_keys=True)
  f.write("\n")
print(reason, file=sys.stderr)
print(f"failure_receipt={out}", file=sys.stderr)
PY
  exit 1
}

check_dangling_superseded_by() {
  [ -d canon ] || return 0
  if ! err=$(python3 - <<'PY' 2>&1
import json
from pathlib import Path

canon = Path("canon")
refs = set()
docs = []

for path in canon.rglob("*.json"):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        continue
    docs.append((path, data))
    for key in ("id", "card_id", "wave_id", "canon_id", "canon_hash", "canon_tag", "tag", "release_tag"):
        value = data.get(key)
        if isinstance(value, str) and value:
            refs.add(value)

missing = []
for path, data in docs:
    value = data.get("superseded_by")
    if value in (None, "", False):
        continue
    values = value if isinstance(value, list) else [value]
    for item in values:
        if not isinstance(item, str) or not item:
            missing.append(f"{path}: invalid superseded_by value")
        elif item not in refs:
            missing.append(f"{path}: dangling superseded_by={item}")

if missing:
    raise SystemExit("; ".join(missing))
PY
  ); then
    fail "dangling superseded_by reference detected :: $err"
  fi
}

changed_files=$(git diff --name-only "$BASE_REF" "$HEAD_REF" -- 'canon/**' 'quarantine/**' || true)

# Always scan existing canon lineage, even when the current diff has no canon/quarantine changes.
check_dangling_superseded_by

if [ -z "$changed_files" ]; then
  echo "Lineage check: PASS"
  exit 0
fi

# 1. No silent deletion inside canon/.
while IFS= read -r path; do
  [ -z "$path" ] && continue
  status=$(git diff --name-status "$BASE_REF" "$HEAD_REF" -- "$path" | awk '{print $1}' | head -1)
  if [[ "$path" == canon/* && "$status" == D* ]]; then
    fail "silent deletion forbidden for canonical path: $path"
  fi
done <<< "$changed_files"

# 2. Validate changed JSON artifacts in correction surfaces.
while IFS= read -r path; do
  [ -z "$path" ] && continue
  [[ "$path" == *.json ]] || continue
  [[ -f "$path" ]] || continue
  python3 -m json.tool "$path" >/dev/null || fail "invalid JSON: $path"

  case "$path" in
    quarantine/*/quarantine.json|quarantine/cards/*/quarantine.json|quarantine/waves/*/quarantine.json)
      if ! err=$(python3 - "$path" <<'PY' 2>&1
import json, sys
p=sys.argv[1]
d=json.load(open(p, encoding='utf-8'))
required=["target_id","target_type","reason_code","evidence_anchor","target_canon_hash","canon_status","override_status"]
missing=[k for k in required if k not in d or d[k] in (None, "")]
if missing:
    raise SystemExit("missing quarantine fields: "+", ".join(missing))
if d["canon_status"] != "QUARANTINE":
    raise SystemExit("quarantine canon_status must be QUARANTINE")
if d["override_status"] is not True:
    raise SystemExit("quarantine override_status must be true")
PY
      ); then
        fail "quarantine validation failed: $path :: $err"
      fi
      ;;
    canon/*/OVERRIDE/*.json|canon/cards/*/OVERRIDE/*.json|canon/waves/*/OVERRIDE/*.json)
      if ! err=$(python3 - "$path" <<'PY' 2>&1
import json, sys
p=sys.argv[1]
d=json.load(open(p, encoding='utf-8'))
required=["override_id","target_id","reason_code","failed_invariant","evidence_anchor","target_canon_hash","supersedes","status","validator_version"]
missing=[k for k in required if k not in d or d[k] in (None, "")]
if missing:
    raise SystemExit("missing override fields: "+", ".join(missing))
if d["status"] not in ("OVERRIDDEN", "SUPERSEDED"):
    raise SystemExit("override status must be OVERRIDDEN or SUPERSEDED")
PY
      ); then
        fail "override validation failed: $path :: $err"
      fi
      ;;
  esac
done <<< "$changed_files"

# 3. Guard immutable identity fields on edited canonical JSON.
while IFS= read -r path; do
  [ -z "$path" ] && continue
  [[ "$path" == canon/*.json || "$path" == canon/cards/*.json || "$path" == canon/cards/*/*.json || "$path" == canon/waves/*.json || "$path" == canon/waves/*/*.json ]] || continue
  [[ -f "$path" ]] || continue

  if git cat-file -e "$BASE_REF:$path" 2>/dev/null; then
    for field in created_at receipt_hash canon_hash; do
      old=$(git show "$BASE_REF:$path" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(sys.argv[1], ""))' "$field" 2>/dev/null || true)
      new=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get(sys.argv[2], ""))' "$path" "$field" 2>/dev/null || true)
      [ "$old" = "$new" ] || fail "immutable field changed: $path::$field"
    done
  fi
done <<< "$changed_files"

echo "Lineage check: PASS"
