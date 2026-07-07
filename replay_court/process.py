#!/usr/bin/env python3
"""Goblin Court Replay Engine v1.

Authority: false.

This runner refuses fake green. It discovers CSV inputs under replay_court/exports,
merges available rows, writes deterministic intermediate artifacts, and blocks final
replay if the required ledger evidence is incomplete.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / "exports"
MERGED = ROOT / "merged"
GRAPHS = ROOT / "graphs"
RECEIPTS = ROOT / "receipts"
CASES = ROOT / "cases"

REQUIRED_LEDGER_FILES = [f"ledger_{i}.csv" for i in range(1, 9)]
AUTHORITY = False


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def discover_csvs() -> list[Path]:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    return sorted(EXPORTS.glob("*.csv"))


def read_rows(files: list[Path]) -> tuple[list[str], list[dict[str, str]]]:
    columns: list[str] = []
    seen_columns: set[str] = set()
    rows: list[dict[str, str]] = []

    for file in files:
        with file.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for field in reader.fieldnames or []:
                if field not in seen_columns:
                    seen_columns.add(field)
                    columns.append(field)
            for row in reader:
                row["source_file"] = file.name
                if "source_file" not in seen_columns:
                    seen_columns.add("source_file")
                    columns.append("source_file")
                rows.append({k: "" if v is None else str(v) for k, v in row.items()})
    return columns, rows


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def exact_dedup(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row in rows:
        key = json.dumps(row, sort_keys=True, separators=(",", ":"))
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def classify(row: dict[str, str]) -> str:
    text = " ".join(str(v).lower() for v in row.values())
    for label in ["approve", "swap", "bridge", "mint", "burn", "transfer", "execute"]:
        if label in text:
            return label
    return "unknown"


def main() -> int:
    for folder in [EXPORTS, MERGED, GRAPHS, RECEIPTS, CASES]:
        folder.mkdir(parents=True, exist_ok=True)

    csvs = discover_csvs()
    present = {p.name for p in csvs}
    missing_ledgers = [name for name in REQUIRED_LEDGER_FILES if name not in present]

    report: dict[str, Any] = {
        "report_id": "REPLAY_EXECUTION_REPORT_V1",
        "series_id": "SERIES-023",
        "work_package": "REPLAY_PROTOCOL_V1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authority": AUTHORITY,
        "checks": [],
    }

    if not csvs:
        report["status"] = "BLOCKED"
        report["reason"] = "No CSV inputs found in replay_court/exports"
        report["checks"].append({"check": "input_discovery", "status": "FAIL", "csv_count": 0})
        write_json(RECEIPTS / "replay_execution_report_v1.json", report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    columns, rows = read_rows(csvs)
    raw_path = MERGED / "merged_raw.csv"
    write_csv(raw_path, columns, rows)

    deduped = exact_dedup(rows)
    dedup_path = MERGED / "merged_dedup.csv"
    write_csv(dedup_path, columns, deduped)

    if "protocol_class" not in columns:
        columns.append("protocol_class")
    classified = []
    for row in deduped:
        new_row = dict(row)
        new_row["protocol_class"] = classify(row)
        classified.append(new_row)

    classified_path = MERGED / "merged_classified.csv"
    canonical_path = MERGED / "jay_unified_ledger.csv"
    write_csv(classified_path, columns, classified)
    write_csv(canonical_path, columns, classified)

    adjacency_path = GRAPHS / "adjacency.csv"
    write_csv(adjacency_path, ["source_file", "protocol_class", "count"], [])

    outputs = [raw_path, dedup_path, classified_path, canonical_path, adjacency_path]
    manifest = {
        "mission": "GOBLIN_COURT_REPLAY_ENGINE",
        "status": "BLOCKED" if missing_ledgers else "COMPLETE",
        "authority": AUTHORITY,
        "inputs": {str(p.relative_to(ROOT)): sha256_file(p) for p in csvs},
        "outputs": {str(p.relative_to(ROOT)): sha256_file(p) for p in outputs},
        "summary": {
            "total_rows": len(rows),
            "deduped_rows": len(deduped),
            "csv_inputs": len(csvs),
            "missing_ledgers": missing_ledgers,
            "protocol_counts": {},
            "case_status": {
                "CASE_001_MISSING_DAYS": "PENDING_FULL_LEDGER_SET",
                "CASE_002_WALLET_3_OAW_PRELIM": "PENDING_FULL_LEDGER_SET",
                "CASE_003_CANONICAL_LEDGER": "PENDING_FULL_LEDGER_SET",
            },
        },
    }
    write_json(RECEIPTS / "receipt_manifest.json", manifest)

    report["status"] = "BLOCKED" if missing_ledgers else "PASS"
    report["reason"] = "Missing required ledger files" if missing_ledgers else "Replay artifacts generated"
    report["checks"] = [
        {"check": "input_discovery", "status": "PASS", "csv_count": len(csvs)},
        {"check": "required_ledgers", "status": "FAIL" if missing_ledgers else "PASS", "missing": missing_ledgers},
        {"check": "raw_merge", "status": "PASS", "rows": len(rows)},
        {"check": "exact_dedup", "status": "PASS", "rows": len(deduped)},
        {"check": "classification", "status": "PASS", "rows": len(classified)},
        {"check": "receipt_manifest", "status": "PASS", "path": "replay_court/receipts/receipt_manifest.json"},
    ]
    write_json(RECEIPTS / "replay_execution_report_v1.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if missing_ledgers else 0


if __name__ == "__main__":
    raise SystemExit(main())
