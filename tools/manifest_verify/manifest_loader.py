"""
Public loader for ReplayOS release manifests.
Parsing is completely independent of verification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

from manifest_schema import ReleaseManifest


class ManifestLoader:
    """
    Loads a release manifest from a file or an in-memory dict.
    """

    @staticmethod
    def load(source: Union[str, Path, Dict[str, Any]]) -> ReleaseManifest:
        """
        Load and parse a release manifest.

        Args:
            source: Path to a JSON file, or an already-parsed dict.

        Returns:
            Fully constructed ReleaseManifest (with _raw preserved).

        Raises:
            FileNotFoundError: if a path is given and does not exist.
            json.JSONDecodeError / ValueError: on malformed input.
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Manifest file not found: {path}")
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        elif isinstance(source, dict):
            data = source
        else:
            raise TypeError(f"Unsupported source type: {type(source)}")

        return ReleaseManifest.from_dict(data)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> ReleaseManifest:
        """Convenience alias for load(dict)."""
        return ManifestLoader.load(data)
