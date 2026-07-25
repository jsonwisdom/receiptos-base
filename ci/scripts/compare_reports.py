#!/usr/bin/env python3
"""
ci/scripts/compare_reports.py

Constitutional conformance comparator — structural protocol-surface only.

Compares exactly these fields and nothing else:
  - fixture_id
  - outcome
  - violation
  - evidence_state
  - replayable

Ignores:
  - validator identity / version
  - timestamps
  - execution time
  - notes
  - host / runtime metadata
  - JSON key order
  - whitespace / formatting differences

On any difference in the protocol surface:
  emit FIELD_MISMATCH and exit non-zero.

On complete identity of the protocol surface:
  exit 0.

No protocol logic beyond structural comparison of the listed fields.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Protocol surface (frozen)
# ---------------------------------------------------------------------------
PROTOCOL_FIELDS = (
    "fixture_id",
    "outcome",
    "violation",
    "evidence_state",
    "replayable",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_reports(directory: Path) -> Dict[str, Dict[str, Any]]:
    """Load all *.json reports under directory, keyed by fixture_id."""
    reports: Dict[str, Dict[str, Any]] = {}
    if not directory.is_dir():
        return reports
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"ERROR: cannot parse {path}: {exc}", file=sys.stderr)
            sys.exit(2)
        fid = data.get("fixture_id")
        if fid is None:
            print(f"ERROR: missing fixture_id in {path}", file=sys.stderr)
            sys.exit(2)
        reports[str(fid)] = data
    return reports


def extract_surface(report: Dict[str, Any]) -> Dict[str, Any]:
    """Return only the protocol-defined fields."""
    return {k: report.get(k) for k in PROTOCOL_FIELDS}


def compare_surfaces(
    ref: Dict[str, Dict[str, Any]], cand: Dict[str, Dict[str, Any]]
) -> List[Tuple[str, str, Any, Any]]:
    """Return list of (fixture_id, field, ref_value, cand_value) mismatches."""
    mismatches: List[Tuple[str, str, Any, Any]] = []

    all_ids = sorted(set(ref) | set(cand))
    for fid in all_ids:
        if fid not in ref:
            mismatches.append((fid, "fixture_id", None, "present only in candidate"))
            continue
        if fid not in cand:
            mismatches.append((fid, "fixture_id", "present only in reference", None))
            continue

        r_surf = extract_surface(ref[fid])
        c_surf = extract_surface(cand[fid])
        for field in PROTOCOL_FIELDS:
            if r_surf[field] != c_surf[field]:
                mismatches.append((fid, field, r_surf[field], c_surf[field]))

    return mismatches


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    # Default locations relative to repository root
    ref_dir = Path("conformance/evidence/reports/ref")
    cand_dir = Path("conformance/evidence/reports/cand")

    # Allow override via environment for CI flexibility
    import os
    ref_dir = Path(os.environ.get("REF_REPORTS_DIR", ref_dir))
    cand_dir = Path(os.environ.get("CAND_REPORTS_DIR", cand_dir))

    ref_reports = load_reports(ref_dir)
    cand_reports = load_reports(cand_dir)

    if not ref_reports and not cand_reports:
        print("NOTE: no reports found in either directory — treating as identity")
        return 0

    mismatches = compare_surfaces(ref_reports, cand_reports)

    if mismatches:
        print("FIELD_MISMATCH")
        for fid, field, rv, cv in mismatches:
            print(f"  fixture_id={fid} field={field} ref={rv!r} cand={cv!r}")
        return 1

    print("CROSS-PASS")
    print(f"  fixtures compared: {len(ref_reports)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
