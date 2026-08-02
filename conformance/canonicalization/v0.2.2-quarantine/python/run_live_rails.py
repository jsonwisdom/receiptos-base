#!/usr/bin/env python3
"""Replay the corrected v0.2.2 quarantine corpus against existing Python rails."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
CORPUS_PATH = Path(__file__).resolve().parents[1] / "corpus" / "corrected-corpus.json"

sys.path.insert(0, str(REPO_ROOT))

from ep.canonical import canonicalize  # noqa: E402
from receiptos.core.hash import canonical_json  # noqa: E402


def _has_unpaired_surrogate(value: Any) -> bool:
    if isinstance(value, str):
        return any(0xD800 <= ord(ch) <= 0xDFFF for ch in value)
    if isinstance(value, list):
        return any(_has_unpaired_surrogate(item) for item in value)
    if isinstance(value, dict):
        return any(
            _has_unpaired_surrogate(key) or _has_unpaired_surrogate(item)
            for key, item in value.items()
        )
    return False


def _run_nfc_receipt(vector: dict[str, Any], value: Any) -> dict[str, Any]:
    try:
        text = canonical_json(value)
        payload = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        error_code = (
            "UNPAIRED_SURROGATE" if _has_unpaired_surrogate(value) else "UTF8_ENCODING_FAILURE"
        )
        matched = (
            vector["expected_result"] == "FAIL"
            and vector.get("expected_error_code") == error_code
        )
        return {
            "id": vector["id"],
            "profile": vector["profile"],
            "actual_result": "FAIL",
            "actual_error_code": error_code,
            "exception_type": type(exc).__name__,
            "matched": matched,
        }

    digest = hashlib.sha256(payload).hexdigest()
    matched = (
        vector["expected_result"] == "PASS"
        and vector.get("expected_output_json") == text
        and vector.get("expected_sha256") == digest
    )
    return {
        "id": vector["id"],
        "profile": vector["profile"],
        "actual_result": "PASS",
        "actual_output_json": text,
        "actual_sha256": digest,
        "matched": matched,
    }


def _run_byte_strict(vector: dict[str, Any], value: Any) -> dict[str, Any]:
    result = canonicalize(value)
    matched = (
        vector["expected_result"] == "PASS"
        and vector.get("expected_output_json") == result.text
        and vector.get("expected_sha256") == result.sha256
    )
    return {
        "id": vector["id"],
        "profile": vector["profile"],
        "actual_result": "PASS",
        "actual_output_json": result.text,
        "actual_sha256": result.sha256,
        "matched": matched,
    }


def main() -> int:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []

    for vector in corpus["vectors"]:
        value = json.loads(vector["input_json"])
        profile = vector["profile"]

        if profile == "JAYWISDOM_NFC_RECEIPT_V1":
            results.append(_run_nfc_receipt(vector, value))
        elif profile == "JAYWISDOM_BYTE_STRICT_EVIDENCE_V1":
            results.append(_run_byte_strict(vector, value))
        else:
            raise RuntimeError(f"Unauthorized profile: {profile}")

    passed = all(item["matched"] for item in results)
    report = {
        "corpus_version": corpus["corpus_version"],
        "runner": "PYTHON_LIVE_RAILS",
        "status": "PASS" if passed else "FAIL",
        "promotion": "PROHIBITED",
        "audit_gate": "410_OPEN",
        "vectors": results,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
