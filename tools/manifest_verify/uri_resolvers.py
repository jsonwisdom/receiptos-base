"""
URI resolution strategies for ReplayOS artifact verification.
Storage-neutral: the verifier never hard-codes scheme logic.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

from manifest_schema import ArtifactRef, ArtifactVerificationStatus


class URIResolver(ABC):
    """Strategy interface for verifying a single ArtifactRef."""

    @abstractmethod
    def supports(self, uri: str) -> bool:
        ...

    @abstractmethod
    def verify(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        """Returns (status, optional human-readable message)."""
        ...


class FileResolver(URIResolver):
    def supports(self, uri: str) -> bool:
        return uri.startswith("file://")

    def verify(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        rel = ref.uri[7:]
        if rel.startswith("/"):
            path = Path(rel)
        else:
            path = base_dir / rel

        if not path.exists():
            return ArtifactVerificationStatus.FAIL, f"File not found: {path}"

        if not ref.digest:
            return ArtifactVerificationStatus.NO_DIGEST, None

        try:
            with open(path, "rb") as f:
                actual = hashlib.sha256(f.read()).hexdigest()
        except OSError as e:
            return ArtifactVerificationStatus.FAIL, f"Cannot read {path}: {e}"

        if actual != ref.digest:
            return (
                ArtifactVerificationStatus.FAIL,
                f"Digest mismatch for {ref.uri}: declared {ref.digest}, computed {actual}",
            )
        return ArtifactVerificationStatus.PASS, None


class IPFSResolver(URIResolver):
    def supports(self, uri: str) -> bool:
        return uri.startswith("ipfs://")

    def verify(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        cid = ref.uri[7:]
        if len(cid) < 10:
            return ArtifactVerificationStatus.FAIL, f"Invalid IPFS CID: {cid}"
        return ArtifactVerificationStatus.PASS, None


class HTTPSResolver(URIResolver):
    def supports(self, uri: str) -> bool:
        return uri.startswith("http://") or uri.startswith("https://")

    def verify(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        if strict and not ref.digest:
            return (
                ArtifactVerificationStatus.FAIL,
                f"HTTPS URI without digest in strict mode: {ref.uri}",
            )
        if ref.digest:
            return ArtifactVerificationStatus.NOT_VERIFIED, "Remote content not fetched"
        return ArtifactVerificationStatus.NO_DIGEST, None


class UnsupportedResolver(URIResolver):
    def supports(self, uri: str) -> bool:
        return True

    def verify(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        return ArtifactVerificationStatus.FAIL, f"Unsupported URI scheme: {ref.uri}"


class URIResolverRegistry:
    """Ordered list of resolvers; first match wins."""

    def __init__(self, resolvers: Optional[list] = None):
        self._resolvers = resolvers or [
            FileResolver(),
            IPFSResolver(),
            HTTPSResolver(),
            UnsupportedResolver(),
        ]

    def resolve(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        for resolver in self._resolvers:
            if resolver.supports(ref.uri or ""):
                return resolver.verify(ref, base_dir, strict=strict)
        return ArtifactVerificationStatus.FAIL, f"No resolver for {ref.uri}"
