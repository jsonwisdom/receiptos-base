"""
ReplayOS Release Manifest schema — pure typed data model.

Responsibilities:
  - represent the manifest structure
  - validate required fields at construction time
  - expose typed objects

Explicitly absent:
  - hashing / canonicalization
  - URI resolution
  - filesystem or network I/O
  - verification logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ── Public status enum (frozen contract) ─────────────────────────────

class ArtifactVerificationStatus(Enum):
    """Stable status values for individual artifact checks."""
    PASS = "PASS"
    FAIL = "FAIL"
    NO_DIGEST = "NO_DIGEST"
    NOT_VERIFIED = "NOT_VERIFIED"


# ── Manifest data model ──────────────────────────────────────────────

@dataclass(frozen=True)
class Integrity:
    algorithm: str = "sha256"
    root_digest: str = ""


@dataclass(frozen=True)
class ArtifactRef:
    """A single content-addressed artifact reference."""
    uri: str
    digest: Optional[str] = None
    media_type: Optional[str] = None
    client: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.uri:
            raise ValueError("ArtifactRef.uri is required")


@dataclass(frozen=True)
class NormativeSection:
    specification: Optional[ArtifactRef] = None
    schemas: tuple = ()
    fixtures: tuple = ()
    generator_contract: Optional[ArtifactRef] = None


@dataclass(frozen=True)
class ExecutionSection:
    reports: tuple = ()
    evidence_bundles: tuple = ()


@dataclass(frozen=True)
class ReleaseManifest:
    """
    Canonical in-memory representation of a release manifest.

    The integrity field is descriptive metadata carried by the manifest;
    recomputation of digests is the responsibility of IntegrityCalculator,
    not this type.
    """
    protocol: Optional[str] = None
    version: Optional[str] = None
    timestamp_utc: Optional[str] = None
    release: Optional[str] = None
    normative: Optional[NormativeSection] = None
    execution: Optional[ExecutionSection] = None
    attestations: tuple = ()
    integrity: Optional[Integrity] = None

    # Preserved for deterministic integrity recomputation by IntegrityCalculator.
    # Not part of the public schema surface for cross-language consumers.
    raw: Optional[Dict[str, Any]] = field(default=None, repr=False, compare=False)

    def all_artifact_refs(self) -> List[ArtifactRef]:
        """Collect every ArtifactRef in document order."""
        refs: List[ArtifactRef] = []
        if self.normative:
            n = self.normative
            if n.specification:
                refs.append(n.specification)
            refs.extend(n.schemas)
            refs.extend(n.fixtures)
            if n.generator_contract:
                refs.append(n.generator_contract)
        if self.execution:
            e = self.execution
            refs.extend(e.reports)
            refs.extend(e.evidence_bundles)
        return refs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReleaseManifest":
        """Construct a typed manifest from a parsed JSON object."""
        if not isinstance(data, dict):
            raise TypeError("manifest data must be a dict")

        def ref(d: Optional[Dict[str, Any]]) -> Optional[ArtifactRef]:
            if not d:
                return None
            return ArtifactRef(
                uri=d.get("uri", ""),
                digest=d.get("digest"),
                media_type=d.get("media_type"),
                client=d.get("client"),
            )

        def ref_list(items: Any) -> tuple:
            if not items:
                return ()
            return tuple(ref(x) for x in items if x)

        integrity_data = data.get("integrity") or {}
        integrity = Integrity(
            algorithm=integrity_data.get("algorithm", "sha256"),
            root_digest=integrity_data.get("root_digest", ""),
        )

        normative_data = data.get("normative") or {}
        normative = NormativeSection(
            specification=ref(normative_data.get("specification")),
            schemas=ref_list(normative_data.get("schemas")),
            fixtures=ref_list(normative_data.get("fixtures")),
            generator_contract=ref(normative_data.get("generator_contract")),
        )

        execution_data = data.get("execution") or {}
        execution = ExecutionSection(
            reports=ref_list(execution_data.get("reports")),
            evidence_bundles=ref_list(execution_data.get("evidence_bundles")),
        )

        return cls(
            protocol=data.get("protocol"),
            version=data.get("version"),
            timestamp_utc=data.get("timestamp_utc"),
            release=data.get("release"),
            normative=normative,
            execution=execution,
            attestations=tuple(data.get("attestations") or ()),
            integrity=integrity,
            raw=dict(data),
        )


# ── Verification result (frozen public contract) ─────────────────────

@dataclass(frozen=True)
class ArtifactCheck:
    """Result of verifying a single artifact reference."""
    uri: str
    status: ArtifactVerificationStatus
    message: Optional[str] = None


@dataclass(frozen=True)
class VerificationResult:
    """
    Stable internal contract shared by all output formatters and the gatekeeper.
    """
    integrity_ok: bool
    artifacts_ok: bool
    errors: tuple = ()
    warnings: tuple = ()
    artifact_checks: tuple = ()

    @property
    def valid(self) -> bool:
        return self.integrity_ok and self.artifacts_ok
