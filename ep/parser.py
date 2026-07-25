"""JSON parser with rich error context."""

import json
from typing import Any


class ParseError(Exception):
    """Raised when JSON parsing fails."""

    def __init__(self, message: str, line: int, column: int):
        self.line = line
        self.column = column
        super().__init__(f"{message} at line {line}, column {column}")


def parse_json(data: bytes) -> dict[str, Any]:
    """
    Parse JSON bytes into a Python dict.

    Args:
        data: UTF-8 encoded JSON bytes

    Returns:
        Parsed dictionary

    Raises:
        ParseError: If JSON is malformed, with line/column context
    """
    try:
        text = data.decode("utf-8")
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ParseError(str(e), e.lineno, e.colno) from e
    except UnicodeDecodeError as e:
        raise ParseError(f"Invalid UTF-8: {e}", 0, 0) from e
