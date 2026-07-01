#!/usr/bin/env python3
"""Create SHA256 checksum sidecars for rendered GPP assets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", required=True, help="Wave id, e.g. W031")
    parser.add_argument("--output-dir", required=True, help="Directory containing rendered PNGs")
    parser.add_argument("--manifest", required=True, help="Output sidecar manifest path")
    parser.add_argument("--prompt", default=None, help="Optional prompt manifest path")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(output_dir.glob("*.png"))
    if not files:
        raise RuntimeError(f"No PNG files found in {output_dir}")

    records: list[dict[str, Any]] = []
    for path in files:
        records.append(
            {
                "wave": args.wave,
                "filename": path.name,
                "path": str(path),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )

    sidecar: dict[str, Any] = {
        "wave": args.wave,
        "asset_count": len(records),
        "assets": records,
    }

    if args.prompt:
        prompt_path = Path(args.prompt)
        if prompt_path.exists():
            prompt_manifest = load_json(prompt_path)
            sidecar["prompt_manifest_sha256"] = sha256_file(prompt_path)
            sidecar["continuity_spec"] = prompt_manifest.get("continuity_spec")
            sidecar["canonical_anchor"] = prompt_manifest.get("canonical_anchor")
            sidecar["release"] = prompt_manifest.get("release")

    manifest_path.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    checksums_path = manifest_path.parent / f"{args.wave.lower()}_checksums.json"
    checksums_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"Wrote {manifest_path}")
    print(f"Wrote {checksums_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
