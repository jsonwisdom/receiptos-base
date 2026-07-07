#!/usr/bin/env python3
"""Observation Protocol V1 packet validator.

Runs two gates:
1. JSON Schema validation for captures and annotations.
2. Cross-file packet linting for references and raw payload hashes.

Certification requires the real `jsonschema` package. No fallback mode is allowed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import jsonschema
except Exception as exc:  # pragma: no cover
    jsonschema = None
    JSONSCHEMA_IMPORT_ERROR = exc
else:
    JSONSCHEMA_IMPORT_ERROR = None

ROOT = Path(__file__).resolve().parents[2]
CAPTURE_SCHEMA_PATH = ROOT / "schemas" / "observation" / "CAPTURE_SCHEMA_V1.json"
ANNOTATION_SCHEMA_PATH = ROOT / "schemas" / "observation" / "ANNOTATION_SCHEMA_V1.json"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def require_jsonschema() -> None:
    if jsonschema is None:
        raise RuntimeError(f"jsonschema not installed: {JSONSCHEMA_IMPORT_ERROR}")


def validate_capture_doc(doc: Dict[str, Any]) -> None:
    require_jsonschema()
    schema = load_json(CAPTURE_SCHEMA_PATH)
    jsonschema.Draft7Validator.check_schema(schema)
    jsonschema.validate(instance=doc, schema=schema)


def validate_annotation_doc(doc: Dict[str, Any]) -> None:
    require_jsonschema()
    schema = load_json(ANNOTATION_SCHEMA_PATH)
    jsonschema.Draft7Validator.check_schema(schema)
    jsonschema.validate(instance=doc, schema=schema)


def gate1_schema_validate(packet_dir: Path) -> List[str]:
    errors: List[str] = []

    for path in sorted((packet_dir / "captures").glob("*.json")):
        try:
            validate_capture_doc(load_json(path))
        except Exception as exc:
            errors.append(f"capture schema failure {path.name}: {exc}")

    for path in sorted((packet_dir / "annotations").glob("*.json")):
        try:
            validate_annotation_doc(load_json(path))
        except Exception as exc:
            errors.append(f"annotation schema failure {path.name}: {exc}")

    return errors


def gate2_packet_lint(packet_dir: Path) -> List[str]:
    errors: List[str] = []
    manifest_path = packet_dir / "packet_manifest.json"
    if not manifest_path.exists():
        return ["missing packet_manifest.json"]

    manifest = load_json(manifest_path)
    if manifest.get("authority") is not False:
        errors.append("packet authority must be false")

    capture_docs = []
    capture_ids = set()
    for rel in manifest.get("captures", []):
        path = packet_dir / rel
        if not path.exists():
            errors.append(f"missing capture path: {rel}")
            continue
        doc = load_json(path)
        capture_docs.append(doc)
        capture_ids.add(doc.get("capture_id"))

    for rel in manifest.get("annotations", []):
        path = packet_dir / rel
        if not path.exists():
            errors.append(f"missing annotation path: {rel}")
            continue
        doc = load_json(path)
        for capture_id in doc.get("referenced_capture_ids", []):
            if capture_id not in capture_ids:
                errors.append(f"annotation {doc.get('annotation_id')} references missing capture_id: {capture_id}")

        if doc.get("confidence_level") == "high":
            has_limitation = bool(doc.get("limitation"))
            for cap in capture_docs:
                if cap.get("capture_id") not in doc.get("referenced_capture_ids", []):
                    continue
                for field in cap.get("fields", []):
                    mutable = field.get("field_replay_class") == "point_in_time"
                    unconfirmed = len(field.get("confirmed_by", [])) == 0
                    if mutable and unconfirmed and not has_limitation:
                        errors.append(
                            f"high-confidence annotation {doc.get('annotation_id')} relies on unconfirmed mutable field {field.get('name')} without limitation"
                        )

    for item in manifest.get("raw_payloads", []):
        rel = item.get("path")
        expected = item.get("sha256")
        path = packet_dir / rel
        if not path.exists():
            errors.append(f"missing raw payload: {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"raw payload hash mismatch for {rel}: expected {expected}, got {actual}")

    return errors


def validate_packet_dir(packet_dir: Path) -> List[str]:
    errors = []
    errors.extend(gate1_schema_validate(packet_dir))
    errors.extend(gate2_packet_lint(packet_dir))
    return errors


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_packet.py <packet_dir>")
        return 2

    packet_dir = Path(argv[1]).resolve()
    errors = validate_packet_dir(packet_dir)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print(f"OK: {packet_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
