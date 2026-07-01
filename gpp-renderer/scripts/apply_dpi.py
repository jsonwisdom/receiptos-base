#!/usr/bin/env python3
"""Apply PNG DPI metadata to rendered assets."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    count = 0
    for path in sorted(Path(args.dir).glob("*.png")):
        with Image.open(path) as img:
            normalized = img.convert("RGBA") if img.mode not in ("RGB", "RGBA") else img.copy()
            normalized.save(path, format="PNG", dpi=(args.dpi, args.dpi))
            count += 1
            print(f"DPI applied: {path}")
    if count == 0:
        raise RuntimeError(f"No PNG files found in {args.dir}")
    print(f"Applied {args.dpi} DPI to {count} PNG files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
