#!/usr/bin/env python3
"""
ACTIVE_LANES v2 validator

Enforces ZTVS invariants on ACTIVE_LANES.md:
- STATUS / STATUS_SOURCE / RECEIPT_PTR triad
- No symbolic receipts
- No manual AUDITOR_VIEW
- authority=false hardened
- GREEN requires VERIFIED_RECEIPT + valid RECEIPT_PTR
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


ACTIVE_LANES_PATH = Path("ACTIVE_LANES.md")

STATUS_VALUES = {"GREEN", "YELLOW", "RED", "NULL"}
STATUS_SOURCE_VALUES = {"VERIFIED_RECEIPT", "REPORTED", "INFERRED", "NULL"}
RECEIPT_PREFIXES = ("sha256:", "tx:", "eas:", "pr:")


class ValidationError(Exception):
    pass


def parse_active_lanes(md_path: Path) -> List[Dict[str, str]]:
    """
    Very small, disciplined parser for v2 lane entries.

    Expected block format:

        LANE: <string>
        STATUS: <enum>
        STATUS_SOURCE: <enum>
        RECEIPT_PTR: <value>
        authority: <true|false>

    Blocks separated by blank lines.
    """
    text = md_path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]

    entries: List[Dict[str, str]] = []
    current: Dict[str, str] = {}

    def flush() -> None:
        nonlocal current
        if current:
            entries.append(current)
            current = {}

    for line in lines:
        if not line.strip():
            flush()
            continue

        match = re.match(r"^([A-Za-z_]+):\s*(.+)$", line)
        if not match:
            continue

        key, value = match.group(1), match.group(2)
        current[key] = value

    flush()
    return entries


def validate_receipt_ptr_format(ptr: str) -> Tuple[bool, str]:
    """Reject symbolic RECEIPT_PTR values and validate allowed formats."""
    if ptr == "NULL":
        return True, ""

    if not any(ptr.startswith(prefix) for prefix in RECEIPT_PREFIXES):
        return False, f"Symbolic or invalid RECEIPT_PTR: {ptr}"

    prefix, payload = ptr.split(":", 1)

    if prefix == "sha256":
        if not re.fullmatch(r"[0-9a-f]{64}", payload):
            return False, f"Invalid sha256 payload length/format: {ptr}"
    elif prefix == "tx":
        if not re.fullmatch(r"0x[0-9a-fA-F]+", payload):
            return False, f"Invalid tx hash format: {ptr}"
    elif prefix == "eas":
        if not re.fullmatch(r"[0-9a-zA-Z\-_:]+", payload):
            return False, f"Invalid eas UID format: {ptr}"
    elif prefix == "pr":
        if not re.fullmatch(r"[0-9]+", payload):
            return False, f"Invalid pr number format: {ptr}"

    return True, ""


def validate_entry(entry: Dict[str, str]) -> List[str]:
    """Apply all rejection rules to a single lane entry."""
    errors: List[str] = []
    lane = entry.get("LANE", "<UNKNOWN>")

    if "AUDITOR_VIEW" in entry:
        errors.append(f"[{lane}] Manual AUDITOR_VIEW present; must be derived, not declared")

    authority = entry.get("authority")
    if authority is None:
        errors.append(f"[{lane}] Missing authority field")
    elif authority.strip().lower() != "false":
        errors.append(f"[{lane}] authority must be 'false', got '{authority}'")

    status = entry.get("STATUS")
    status_source = entry.get("STATUS_SOURCE")
    receipt_ptr = entry.get("RECEIPT_PTR")

    if status is None:
        errors.append(f"[{lane}] Missing STATUS")
    elif status not in STATUS_VALUES:
        errors.append(f"[{lane}] Invalid STATUS '{status}'")

    if status_source is None:
        errors.append(f"[{lane}] Missing STATUS_SOURCE")
    elif status_source not in STATUS_SOURCE_VALUES:
        errors.append(f"[{lane}] Invalid STATUS_SOURCE '{status_source}'")

    if receipt_ptr is None:
        errors.append(f"[{lane}] Missing RECEIPT_PTR")
    else:
        ok, msg = validate_receipt_ptr_format(receipt_ptr)
        if not ok:
            errors.append(f"[{lane}] {msg}")

    if status == "GREEN" and status_source != "VERIFIED_RECEIPT":
        errors.append(
            f"[{lane}] STATUS=GREEN requires STATUS_SOURCE=VERIFIED_RECEIPT; "
            f"got STATUS_SOURCE={status_source}"
        )

    if status_source == "VERIFIED_RECEIPT" and receipt_ptr == "NULL":
        errors.append(f"[{lane}] VERIFIED_RECEIPT requires non-NULL RECEIPT_PTR")

    return errors


def validate_ext_001_schema(entries: List[Dict[str, str]]) -> List[str]:
    """Enforce a minimal strict field membrane for lane entries."""
    errors: List[str] = []
    allowed_keys = {
        "LANE",
        "STATUS",
        "STATUS_SOURCE",
        "RECEIPT_PTR",
        "authority",
    }

    for entry in entries:
        lane = entry.get("LANE", "<UNKNOWN>")
        for key in entry.keys():
            if key not in allowed_keys:
                errors.append(f"[{lane}] Unknown field '{key}' not in EXT-001 schema")

    return errors


def main() -> int:
    if not ACTIVE_LANES_PATH.exists():
        print(f"FAIL: ACTIVE_LANES.md not found at {ACTIVE_LANES_PATH}", file=sys.stderr)
        return 1

    entries = parse_active_lanes(ACTIVE_LANES_PATH)

    if not entries:
        print("FAIL: No lane entries found in ACTIVE_LANES.md", file=sys.stderr)
        return 1

    all_errors: List[str] = []

    for entry in entries:
        all_errors.extend(validate_entry(entry))

    all_errors.extend(validate_ext_001_schema(entries))

    if all_errors:
        print("FAIL:")
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
