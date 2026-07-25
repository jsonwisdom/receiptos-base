"""Canonical JSON serialization per M1 contract.

Contract (integer-only, deterministic):
- UTF-8, no BOM
- Object keys sorted lexicographically by Unicode code point (recursive)
- Arrays preserved in original order
- No insignificant whitespace
- Solidus (/) is NOT escaped
- No Unicode normalization (raw code points after parsing)
- Integers only — floats are rejected (EP v1.0.0 integer-only rule)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CanonicalResult:
    """Result of canonicalizing a JSON value."""

    bytes: bytes
    """UTF-8 canonical bytes."""

    text: str
    """Canonical text representation."""

    @property
    def sha256(self) -> str:
        """SHA-256 hex digest of the canonical bytes."""
        return hashlib.sha256(self.bytes).hexdigest()


def canonicalize(value: Any) -> CanonicalResult:
    """
    Serialize a JSON value to canonical form.

    Raises:
        TypeError: If value contains a float or any non-JSON type.
    """
    text = _canonicalize_value(value)
    return CanonicalResult(bytes=text.encode("utf-8"), text=text)


def _canonicalize_value(value: Any) -> str:
    """Internal recursive canonical serializer."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        # Must check bool before int (bool is a subclass of int).
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        # Explicit rejection: EP v1.0.0 is integer-only.
        raise TypeError(
            "Floating-point numbers are not permitted under the EP M1 "
            "integer-only canonicalization contract"
        )
    if isinstance(value, str):
        return _canonicalize_string(value)
    if isinstance(value, list):
        return "[" + ",".join(_canonicalize_value(v) for v in value) + "]"
    if isinstance(value, dict):
        items = sorted(value.items(), key=lambda kv: kv[0])
        return "{" + ",".join(
            f"{_canonicalize_string(k)}:{_canonicalize_value(v)}"
            for k, v in items
        ) + "}"
    raise TypeError(f"Unsupported JSON type: {type(value)}")


def _canonicalize_string(s: str) -> str:
    """Canonical string serialization (no solidus escaping, raw UTF-8)."""
    result = ['"']
    for ch in s:
        code = ord(ch)
        if code == 0x08:  # \b
            result.append("\\b")
        elif code == 0x0C:  # \f
            result.append("\\f")
        elif code == 0x0A:  # \n
            result.append("\\n")
        elif code == 0x0D:  # \r
            result.append("\\r")
        elif code == 0x09:  # \t
            result.append("\\t")
        elif ch == "\\":
            result.append("\\\\")
        elif ch == '"':
            result.append('\\"')
        elif 0x00 <= code <= 0x1F:
            result.append(f"\\u{code:04x}")
        else:
            # Raw UTF-8 character (including solidus / and non-ASCII).
            result.append(ch)
    result.append('"')
    return "".join(result)
