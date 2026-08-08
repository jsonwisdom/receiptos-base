"""Fail-closed vendored schema/spec pin verification for Agent Economics V0.1."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

SOURCE_REPOSITORY = "jsonwisdom/AL"
SOURCE_BRANCH = "agent/jaywisdom-agent-economics-v0-1"
SOURCE_COMMIT = "af63889a692890cfd0e3ed74224b4feb1b614ac4"

# Git blob object IDs: SHA1("blob " + byte_length + NUL + file_bytes).
EXPECTED_GIT_BLOB_SHA1 = {
    "JAYWISDOM_AGENT_ECONOMICS_V0_1.schema.json": "4ac089aa4824820634665f78a59b70e709c87292",
    "ECONOMIC_DECISION_RECEIPT_V0_1.schema.json": "0cf20aebc909b2f311868efdcf872b0f53af47ee",
    "REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1.schema.json": "bedfcca08ea9c4aa73ca2f68510a65dd58cb5ad2",
    "JAYWISDOM_AGENT_ECONOMIC_GATE_V0_1.md": "ecd02c3b5f299c506b7638ef68f6b92b4f7a1b01",
}

# Plain SHA-256 over the exact UTF-8 file bytes.
EXPECTED_SHA256 = {
    "JAYWISDOM_AGENT_ECONOMICS_V0_1.schema.json": "dbd0c30a1e916b0cce53f5ca102d0274d6438437cd163b00dca321b25de0c171",
    "ECONOMIC_DECISION_RECEIPT_V0_1.schema.json": "e85f4a806be8d25bcc48a290061b3a770ff708ffe3bd04f74f03589f27fa32a1",
    "REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1.schema.json": "179df010c0ec1b657f1ea60b6d2265c2c83ef8f40fd88b6822a741794e77468a",
    "JAYWISDOM_AGENT_ECONOMIC_GATE_V0_1.md": "8922866e176ad55f26c0045d4e3638cb69863fc81c737512f2ffaf9292baf5ba",
}


class SchemaPinError(RuntimeError):
    """Raised when vendored truth-contract bytes are absent or drifted."""


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def verify_schema_pin(schema_dir: Path | None = None) -> Dict[str, Dict[str, str]]:
    """Verify exact vendored bytes against both pinned digest families.

    Any missing or drifted file raises SchemaPinError. Passing this function
    proves byte equality only; it creates no execution authority.
    """
    root = schema_dir or (Path(__file__).resolve().parent / "schemas")
    report: Dict[str, Dict[str, str]] = {}
    errors = []

    for name, expected_blob in EXPECTED_GIT_BLOB_SHA1.items():
        path = root / name
        if not path.is_file():
            errors.append(f"MISSING:{name}")
            continue
        data = path.read_bytes()
        actual_blob = git_blob_sha1(data)
        actual_sha256 = hashlib.sha256(data).hexdigest()
        report[name] = {
            "git_blob_sha1": actual_blob,
            "sha256": actual_sha256,
        }
        if actual_blob != expected_blob:
            errors.append(
                f"GIT_BLOB_DRIFT:{name}:expected={expected_blob}:actual={actual_blob}"
            )
        expected_sha256 = EXPECTED_SHA256[name]
        if actual_sha256 != expected_sha256:
            errors.append(
                f"SHA256_DRIFT:{name}:expected={expected_sha256}:actual={actual_sha256}"
            )

    if errors:
        raise SchemaPinError(";".join(errors))
    return report
