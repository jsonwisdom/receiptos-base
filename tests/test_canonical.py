"""Tests for canonicalization per M1 contract."""

import json
from pathlib import Path

import pytest

from ep.canonical import canonicalize
from ep.parser import parse_json

FIXTURES = Path(__file__).parent / "fixtures" / "canonical"


# ---------------------------------------------------------------------------
# Expected canonical forms for the normative fixtures
# ---------------------------------------------------------------------------

EXPECTED = {
    "object-order.json": (
        '{"a":1,"b":2,"c":3}',
        # sha256 of the UTF-8 bytes of the above string
    ),
    "unicode.json": (
        '{"emoji":"🚀","mixed":"naïve","text":"café"}',
    ),
    "escapes.json": (
        '{"backslash":"path\\\\to\\\\file","control":"hello\\nworld\\t!",'
        '"quotes":"say \\"hello\\"","solidus":"/usr/bin"}',
    ),
    "nested.json": (
        '{"array":[{"a":1,"b":2},null,false],'
        '"outer":{"a":{"nested":true,"value":42},"z":[3,1,2]}}',
    ),
}


def _load_fixture(name: str):
    return parse_json((FIXTURES / name).read_bytes())


def test_canonical_sorts_keys():
    result = canonicalize({"b": 2, "a": 1, "c": 3})
    assert result.text == '{"a":1,"b":2,"c":3}'


def test_canonical_removes_whitespace():
    result = canonicalize({"a": 1})
    assert " " not in result.text
    assert "\n" not in result.text
    assert "\t" not in result.text


def test_canonical_does_not_escape_solidus():
    result = canonicalize({"path": "/usr/bin"})
    assert "/" in result.text
    assert "\\/" not in result.text


def test_canonical_preserves_array_order():
    result = canonicalize({"array": [3, 1, 2]})
    assert result.text == '{"array":[3,1,2]}'


def test_canonical_preserves_unicode_raw():
    result = canonicalize({"text": "é"})
    assert "é" in result.text
    assert "\\u00e9" not in result.text


def test_canonical_handles_control_characters():
    result = canonicalize({"text": "hello\nworld"})
    assert "\\n" in result.text


def test_canonical_handles_quotes_and_backslashes():
    result = canonicalize({"text": 'hello "world" \\'})
    assert '\\"' in result.text
    assert "\\\\" in result.text


def test_canonical_roundtrip():
    input_dict = {
        "b": 2,
        "a": {"nested": True, "array": [3, 1, 2], "text": "é"},
    }
    result = canonicalize(input_dict)
    parsed = json.loads(result.text)
    assert parsed == input_dict


def test_canonical_rejects_float():
    with pytest.raises(TypeError, match="integer-only|Floating-point"):
        canonicalize({"value": 3.14})


@pytest.mark.parametrize(
    "value",
    [
        {"a": 1},
        {"b": 2, "a": 1},
        {"array": [1, 2, 3]},
        {"nested": {"deep": {"deeper": True}}},
        {"text": "hello world"},
        {"unicode": "éèê"},
        {"control": "hello\nworld"},
        {"path": "/usr/bin"},
        {"mixed": {"b": 2, "a": 1, "array": [3, 1, 2]}},
        None,
        True,
        False,
        0,
        42,
        [],
        {},
    ],
)
def test_canonical_deterministic(value):
    """Same input always produces identical canonical bytes and SHA-256."""
    r1 = canonicalize(value)
    r2 = canonicalize(value)
    assert r1.bytes == r2.bytes
    assert r1.sha256 == r2.sha256
    # Round-trip stability
    parsed = json.loads(r1.text)
    r3 = canonicalize(parsed)
    assert r1.bytes == r3.bytes


# ---------------------------------------------------------------------------
# Normative fixture tests — bytes + SHA-256
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_canonical_fixture_bytes(name: str):
    value = _load_fixture(name)
    result = canonicalize(value)
    expected_text = EXPECTED[name][0]
    assert result.text == expected_text
    assert result.bytes == expected_text.encode("utf-8")


@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_canonical_fixture_sha256(name: str):
    value = _load_fixture(name)
    result = canonicalize(value)
    # Recompute expected SHA-256 from the frozen expected text
    import hashlib
    expected_digest = hashlib.sha256(
        EXPECTED[name][0].encode("utf-8")
    ).hexdigest()
    assert result.sha256 == expected_digest


def test_canonical_fixture_object_order_sha256_known():
    """Explicit known-good SHA-256 for the simplest normative fixture."""
    value = _load_fixture("object-order.json")
    result = canonicalize(value)
    # Frozen: sha256 of UTF-8 bytes of {"a":1,"b":2,"c":3}
    assert result.sha256 == (
        "e6a3385fb77c287a712e7f406a451727f0625041823ecf23bea7ef39b2e39805"
    )
