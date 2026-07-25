"""Publisher contract and reference implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from attestation_schema import AttestationResult


class Publisher(ABC):
    @abstractmethod
    def publish(self, artifact_path: Path, result: AttestationResult) -> bool:
        ...


class LocalFilesystemPublisher(Publisher):
    def __init__(self, dest_dir: Path):
        self.dest_dir = Path(dest_dir)

    def publish(self, artifact_path: Path, result: AttestationResult) -> bool:
        try:
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            dest = self.dest_dir / artifact_path.name
            dest.write_bytes(artifact_path.read_bytes())
            print(f"  📁 Published {artifact_path.name} → {dest}")
            return True
        except OSError as e:
            print(f"  ✗ Filesystem publish failed: {e}")
            return False
