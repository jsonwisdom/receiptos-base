#!/usr/bin/env python3
"""Sanitize ReplayBoard JSON/JSONL artifacts before LLM review.

Design axiom:

    LLMs review the shape. Replay verifies the truth.

This utility preserves receipt structure, schema versions, hashes, status fields,
and invariant flags while redacting secrets and local-only values. It is a local
semantic-review preprocessor, not an attestation artifact.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any, Dict, List, Optional

SANITIZER_VERSION = "REPLAYBOARD_LLM_SANITIZER_V1"
MAX_TEXT_BYTES = 10_000_000

PRESERVE_EXACT_FIELDS = {
    "authority",
    "body_size_bytes",
    "canonicalizer_version",
    "chain_id",
    "claim_id",
    "content_hash",
    "created_at",
    "eas_schema_name",
    "eas_schema_uid",
    "eas_uid",
    "error",
    "fail_closed",
    "final_url",
    "hash_method",
    "invariants",
    "ledger_tip_hash",
    "prev_receipt_hash",
    "reason",
    "receipt_hash",
    "replayable",
    "resolution",
    "schema_uid",
    "schema_version",
    "settle_condition_url",
    "source_ref",
    "source_repo",
    "status",
    "status_code",
    "truth_claim",
    "verifier_version",
    "witness_only",
}

REDACT_FIELD_FRAGMENTS = {
    "authorization",
    "bearer",
    "client_secret",
    "cookie",
    "credential",
    "jwt",
    "local_path",
    "mnemonic",
    "password",
    "private_key",
    "raw_artifact_path",
    "raw_body",
    "raw_evidence",
    "refresh_token",
    "secret",
    "seed_phrase",
    "session",
    "token",
    "api_key",
}

SENSITIVE_PATTERNS: List[tuple[str, re.Pattern[str]]] = [
    ("BEARER_TOKEN", re.compile(r"Bearer\s+[^\s]+", re.IGNORECASE)),
    ("JWT_LIKE", re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    ("PRIVATE_HEX_64", re.compile(r"(?<![A-Fa-f0-9])(?:0x)?[A-Fa-f0-9]{64}(?![A-Fa-f0-9])")),
    ("EMAIL", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
]

HASH_PATTERN = re.compile(r"^sha256:[A-Fa-f0-9]{64}$")
HEX_32_PATTERN = re.compile(r"^0x[A-Fa-f0-9]{64}$")
HEX_ADDRESS_PATTERN = re.compile(r"^0x[A-Fa-f0-9]{40}$")


class SanitizeError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def looks_binary(data: bytes) -> bool:
    if b"\x00" in data:
        return True
    sample = data[:4096]
    if not sample:
        return False
    non_text = sum(1 for byte in sample if byte < 9 or (13 < byte < 32))
    return non_text / len(sample) > 0.05


def should_redact_key(key: Optional[str]) -> bool:
    if not key:
        return False
    lowered = key.lower()
    return any(fragment in lowered for fragment in REDACT_FIELD_FRAGMENTS)


def redact_string(value: str) -> str:
    if HASH_PATTERN.match(value) or HEX_32_PATTERN.match(value) or HEX_ADDRESS_PATTERN.match(value):
        return value

    redacted = value
    for label, pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(f"[REDACTED_{label}]", redacted)
    return redacted


def sanitize_value(value: Any, key: Optional[str] = None) -> Any:
    if key in PRESERVE_EXACT_FIELDS:
        if isinstance(value, str):
            return redact_string(value)
        if isinstance(value, dict):
            return {child_key: sanitize_value(child_value, child_key) for child_key, child_value in value.items()}
        if isinstance(value, list):
            return [sanitize_value(item, None) for item in value]
        return value

    if should_redact_key(key):
        return f"[REDACTED_{key.upper()}]"

    if isinstance(value, dict):
        return {child_key: sanitize_value(child_value, child_key) for child_key, child_value in value.items()}
    if isinstance(value, list):
        return [sanitize_value(item, None) for item in value]
    if isinstance(value, str):
        return redact_string(value)
    return value


def parse_json_or_jsonl(text: str) -> List[Any]:
    stripped = text.strip()
    if not stripped:
        raise SanitizeError("EMPTY_INPUT")

    try:
        parsed = json.loads(stripped)
        return [parsed]
    except json.JSONDecodeError:
        rows: List[Any] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({
                    "line_number": line_number,
                    "log_line": redact_string(line),
                    "non_json": True,
                })
        if not rows:
            raise SanitizeError("NO_PARSEABLE_LINES")
        return rows


def sanitize_file(input_path: pathlib.Path) -> Dict[str, Any]:
    data = input_path.read_bytes()
    if len(data) > MAX_TEXT_BYTES:
        raise SanitizeError(f"INPUT_TOO_LARGE bytes={len(data)} max={MAX_TEXT_BYTES}")
    if looks_binary(data):
        raise SanitizeError("BINARY_INPUT_REFUSED use metadata/ledger only, never evidence.bin")

    text = data.decode("utf-8")
    rows = parse_json_or_jsonl(text)
    sanitized_rows = [sanitize_value(row, None) for row in rows]

    return {
        "schema_version": "receiptos.llm_review_bundle.v0.1",
        "sanitizer_version": SANITIZER_VERSION,
        "source_path_hint": str(input_path),
        "record_count": len(sanitized_rows),
        "records": sanitized_rows,
        "axiom": "LLMs review the shape. Replay verifies the truth.",
    }


def assert_no_sensitive_patterns(bundle: Dict[str, Any]) -> None:
    rendered = canonical_json(bundle)
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(rendered):
            raise SanitizeError(f"SANITIZER_LEAK_DETECTED pattern={label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize ReplayBoard artifacts for LLM review")
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()

    bundle = sanitize_file(args.input)
    assert_no_sensitive_patterns(bundle)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(canonical_json(bundle) + "\n", encoding="utf-8")

    print("REPLAYBOARD_LLM_SANITIZER=PASS")
    print(f"REPLAYBOARD_LLM_REVIEW_BUNDLE={args.out}")
    print(f"REPLAYBOARD_LLM_RECORDS={bundle['record_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
