"""AuthorizationReceipt boundary validation (M7).

Enforces the normative schema surface and the subset of invariants that apply
directly to AuthorizationReceipt artifacts:
- M7-002: exactly one subject_decision_id
- M7-005: authorization_context_hash is well-formed SHA-256
- M7-007: signature present and non-empty (immutability is a post-issuance property)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

SHA256_HEX = re.compile(r"^[a-f0-9]{64}$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

ALLOWED_AUTH_TYPES = {"InitialLock", "ReLock", "Override", "Emergency"}

REQUIRED_FIELDS = [
    "receipt_id",
    "issued_at",
    "issuer",
    "subject_decision_id",
    "authorization_context_hash",
    "authorization_type",
    "supporting_evidence_hashes",
    "signature",
]


class AuthorizationReceiptValidator:
    """Validates a single AuthorizationReceipt object."""

    def validate(self, receipt: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        # Presence of required fields
        for field in REQUIRED_FIELDS:
            if field not in receipt:
                errors.append(f"missing required field: {field}")

        if errors:
            return False, errors

        # receipt_id format (UUIDv4 preferred)
        if not UUID_RE.match(str(receipt["receipt_id"])):
            errors.append("receipt_id is not a valid UUID")

        # authorization_type enum
        if receipt["authorization_type"] not in ALLOWED_AUTH_TYPES:
            errors.append(
                f"authorization_type must be one of {sorted(ALLOWED_AUTH_TYPES)}"
            )

        # M7-002: exactly one subject_decision_id (scalar non-empty string)
        sdi = receipt["subject_decision_id"]
        if not isinstance(sdi, str) or not sdi.strip():
            errors.append("M7-002: subject_decision_id must be a non-empty string")

        # M7-005: authorization_context_hash is SHA-256 hex
        if not SHA256_HEX.match(str(receipt["authorization_context_hash"])):
            errors.append("M7-005: authorization_context_hash must be 64-char hex SHA-256")

        # supporting_evidence_hashes
        seh = receipt["supporting_evidence_hashes"]
        if not isinstance(seh, list):
            errors.append("supporting_evidence_hashes must be an array")
        else:
            for h in seh:
                if not SHA256_HEX.match(str(h)):
                    errors.append(f"supporting_evidence_hashes contains non-SHA-256 value: {h}")

        # M7-007: signature present and non-empty
        sig = receipt["signature"]
        if not isinstance(sig, str) or not sig.strip():
            errors.append("M7-007: signature must be a non-empty string")

        return len(errors) == 0, errors
