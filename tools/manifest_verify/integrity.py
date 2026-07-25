"""
Public integrity computation for ReplayOS manifests.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional, Tuple


class IntegrityCalculator:
    """
    Computes and verifies the root integrity digest of a release manifest.

    Public API only — no private helpers exposed to callers.
    """

    SUPPORTED_ALGORITHMS = {"sha256"}

    def compute(self, data: Dict[str, Any], algorithm: str = "sha256") -> str:
        """
        Compute the root digest over a manifest dict with the integrity
        field excluded. Uses canonical JSON serialisation.
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        payload = dict(data)
        payload.pop("integrity", None)

        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def verify(
        self,
        data: Dict[str, Any],
        declared_digest: str,
        algorithm: str = "sha256",
    ) -> Tuple[bool, Optional[str]]:
        """
        Recompute the root digest and compare against the declared value.

        Returns (ok, error_message).
        """
        if not declared_digest:
            return False, "Manifest missing 'integrity.root_digest'"

        try:
            computed = self.compute(data, algorithm=algorithm)
        except ValueError as e:
            return False, str(e)

        if computed != declared_digest:
            return False, (
                f"Integrity mismatch: declared {declared_digest}, "
                f"computed {computed}"
            )
        return True, None
