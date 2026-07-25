"""Tests for JSON parser."""

from pathlib import Path

import pytest

from ep.parser import ParseError, parse_json


def test_parser_accepts_valid_json():
    data = b'{"id": "obs-001", "timestamp": 1234567890}'
    result = parse_json(data)
    assert result["id"] == "obs-001"
    assert result["timestamp"] == 1234567890


def test_parser_rejects_malformed_json():
    data = b'{"id": "obs-001", "timestamp": }'
    with pytest.raises(ParseError) as exc:
        parse_json(data)
    assert exc.value.line > 0
    assert "line" in str(exc.value).lower()


def test_parser_rejects_invalid_utf8():
    data = b'{"key": "value\xff"}'
    with pytest.raises(ParseError) as exc:
        parse_json(data)
    assert "UTF-8" in str(exc.value)


def test_parser_loads_obs001_fixture():
    fixture_path = (
        Path(__file__).parent / "fixtures" / "OBS-001-minimal-observed.json"
    )
    data = fixture_path.read_bytes()
    result = parse_json(data)
    assert isinstance(result, dict)
    assert result["id"] == "obs-001"
    assert result["timestamp"] == 1700000000
