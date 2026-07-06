#!/usr/bin/env python3
"""Negative fixture certification harness for Observation Protocol V1.

This script generates a positive packet and six negative mutations. It requires
jsonschema because certification must not run in fallback mode.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tests" / "observation" / "validate_packet.py"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_packet() -> Path:
    raw_text = "raw observation payload for packet demo\n"
    raw_hash = sha256_text(raw_text)

    tmp = Path(tempfile.mkdtemp(prefix="obs_packet_"))
    packet = tmp / "packet_demo_PKT-747-002-0001"
    (packet / "raw").mkdir(parents=True)
    (packet / "captures").mkdir(parents=True)
    (packet / "annotations").mkdir(parents=True)
    (packet / "raw" / "raw_payload_001.txt").write_text(raw_text, encoding="utf-8")

    capture = {
        "capture_id": "CAP-747-002-0001",
        "authority": False,
        "chain_id": 8453,
        "contract_address": "0x0000000000000000000000000000000000000001",
        "block_number": 1,
        "block_hash": "0x" + "a" * 64,
        "tx_hash": "0x" + "b" * 64,
        "capture_timestamp_utc": "2026-07-06T00:00:00Z",
        "observer_id": "jsonwisdom-run2",
        "capture_method": "generated-demo-fixture",
        "source_type": "json",
        "source_url_or_endpoint": "local-fixture://raw/raw_payload_001.txt",
        "raw_payload_sha256": raw_hash,
        "independent_confirmation_required": True,
        "fields": [
            {
                "name": "contract_address",
                "observed": True,
                "value": "0x0000000000000000000000000000000000000001",
                "field_replay_class": "immutable",
                "confirmed_by": ["generated-demo-fixture"],
                "confirmation_depth_at_capture": 12
            },
            {
                "name": "holder_count_displayed",
                "observed": False,
                "value": None,
                "field_replay_class": "point_in_time",
                "confirmed_by": [],
                "confirmation_depth_at_capture": 12
            }
        ]
    }

    annotation = {
        "annotation_id": "ANN-747-002-0001",
        "authority": False,
        "referenced_capture_ids": ["CAP-747-002-0001"],
        "annotation_type": "limitation",
        "claim_text": "Holder count was not observed in this capture and must not be inferred as zero.",
        "confidence_level": "low",
        "evidence_basis": ["CAP-747-002-0001"],
        "falsifiable_prediction": None,
        "expected_observation": None,
        "failure_condition": None,
        "limitation": "This annotation records absence of displayed data, not absence of holders.",
        "created_by": "jsonwisdom-run2",
        "created_at_utc": "2026-07-06T00:00:00Z"
    }

    manifest = {
        "packet_id": "PKT-747-002-0001",
        "authority": False,
        "captures": ["captures/capture_001.json"],
        "annotations": ["annotations/annotation_001.json"],
        "raw_payloads": [{"path": "raw/raw_payload_001.txt", "sha256": raw_hash}],
        "created_at_utc": "2026-07-06T00:00:00Z"
    }

    write_json(packet / "captures" / "capture_001.json", capture)
    write_json(packet / "annotations" / "annotation_001.json", annotation)
    write_json(packet / "packet_manifest.json", manifest)
    return packet


def clone_packet(packet: Path, label: str) -> Path:
    parent = Path(tempfile.mkdtemp(prefix=f"obs_{label}_"))
    dst = parent / packet.name
    shutil.copytree(packet, dst)
    return dst


def run_validator(packet: Path) -> Tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(packet)],
        cwd=str(ROOT),
        text=True,
        capture_output=True
    )
    return proc.returncode, proc.stdout + proc.stderr


def load_capture(packet: Path) -> Tuple[Path, Dict[str, Any]]:
    path = packet / "captures" / "capture_001.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def load_annotation(packet: Path) -> Tuple[Path, Dict[str, Any]]:
    path = packet / "annotations" / "annotation_001.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def expect(name: str, ok: bool, output: str = "") -> bool:
    print(("PASS" if ok else "FAIL") + " - " + name)
    if not ok and output:
        print(output[-1200:])
    return ok


def main() -> int:
    try:
        import jsonschema  # noqa: F401
    except Exception as exc:
        print(f"FAIL - jsonschema unavailable: {exc}")
        print("CERTIFICATION FAILED. Do not tag observation-protocol-v1.")
        return 1

    checks = []
    base = make_packet()

    code, out = run_validator(base)
    checks.append(expect("positive packet passes", code == 0, out))

    tampered = clone_packet(base, "tamper")
    raw = tampered / "raw" / "raw_payload_001.txt"
    raw.write_text(raw.read_text(encoding="utf-8") + "TAMPER\n", encoding="utf-8")
    code, out = run_validator(tampered)
    checks.append(expect("tampered raw payload fails", code != 0, out))

    missing_ref = clone_packet(base, "missingref")
    path, ann = load_annotation(missing_ref)
    ann["referenced_capture_ids"] = ["CAPTURE-DOES-NOT-EXIST"]
    write_json(path, ann)
    code, out = run_validator(missing_ref)
    checks.append(expect("missing capture_id fails", code != 0, out))

    authority = clone_packet(base, "authority")
    path, ann = load_annotation(authority)
    ann["authority"] = True
    write_json(path, ann)
    code, out = run_validator(authority)
    checks.append(expect("authority:true fails", code != 0, out))

    observed = clone_packet(base, "observed")
    path, cap = load_capture(observed)
    cap["fields"][0]["observed"] = False
    cap["fields"][0]["value"] = "SHOULD_BE_NULL"
    write_json(path, cap)
    code, out = run_validator(observed)
    checks.append(expect("observed:false with value fails", code != 0, out))

    notes = clone_packet(base, "notes")
    path, cap = load_capture(notes)
    cap["notes"] = "interpretive leakage"
    write_json(path, cap)
    code, out = run_validator(notes)
    checks.append(expect("capture notes field fails", code != 0, out))

    no_refs = clone_packet(base, "nocaprefs")
    path, ann = load_annotation(no_refs)
    ann["referenced_capture_ids"] = []
    write_json(path, ann)
    code, out = run_validator(no_refs)
    checks.append(expect("empty referenced_capture_ids fails", code != 0, out))

    passed = sum(1 for item in checks if item)
    total = len(checks)
    print(f"\n{passed}/{total} checks passed.")

    if passed != total:
        print("CERTIFICATION FAILED. Do not tag observation-protocol-v1.")
        return 1

    print("CERTIFICATION PASSED. Eligible for validation log + tag.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
