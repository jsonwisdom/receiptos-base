#!/usr/bin/env python3
"""No-cost deterministic renderer for GPP pipeline validation.

This creates simple 2048x2048 PNG proof cards from the prompt manifest without using
Replicate or any paid image API. It is for pipeline validation, layout previews, Drive
upload tests, and checksum flow.
"""
from __future__ import annotations

import argparse
import json
import textwrap
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

CANVAS = 2048
DPI = 300
BG = (241, 196, 15)
PAPER = (246, 239, 210)
INK = (28, 40, 51)
RED = (180, 55, 45)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def font(size: int):
    for candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        p = Path(candidate)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, font_obj, fill=INK, line_gap=10) -> int:
    x, y = xy
    avg_chars = max(18, width // max(1, int(font_obj.size * 0.58)))
    for line in textwrap.wrap(text, width=avg_chars):
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += font_obj.size + line_gap
    return y


def render_card(card: dict[str, Any], wave_title: str, out_path: Path) -> None:
    img = Image.new("RGB", (CANVAS, CANVAS), BG)
    draw = ImageDraw.Draw(img)

    # Outer card and inner scumline.
    margin = 80
    draw.rounded_rectangle([margin, margin, CANVAS - margin, CANVAS - margin], radius=70, fill=PAPER, outline=INK, width=18)
    draw.rounded_rectangle([margin + 35, margin + 35, CANVAS - margin - 35, CANVAS - margin - 35], radius=45, outline=INK, width=7)

    title_font = font(118)
    subtitle_font = font(52)
    body_font = font(48)
    small_font = font(34)

    title = card["title"]
    one_liner = card.get("one_liner", "")
    vector = card.get("vector", "")
    system = card.get("system", "")
    card_id = card["card_id"]
    gag = card.get("hidden_gag_grid", "")

    # Top banner.
    draw.rectangle([120, 120, CANVAS - 120, 280], fill=INK)
    draw.text((150, 145), wave_title.upper(), font=subtitle_font, fill=PAPER)
    draw.text((CANVAS - 460, 145), card_id, font=small_font, fill=PAPER)

    # Central symbolic goblin placeholder.
    cx, cy = CANVAS // 2, 880
    draw.ellipse([cx - 260, cy - 260, cx + 260, cy + 260], fill=(142, 172, 91), outline=INK, width=14)
    draw.polygon([(cx - 210, cy - 170), (cx - 330, cy - 360), (cx - 80, cy - 250)], fill=(142, 172, 91), outline=INK)
    draw.polygon([(cx + 210, cy - 170), (cx + 330, cy - 360), (cx + 80, cy - 250)], fill=(142, 172, 91), outline=INK)
    draw.ellipse([cx - 120, cy - 60, cx - 55, cy + 5], fill=INK)
    draw.ellipse([cx + 55, cy - 60, cx + 120, cy + 5], fill=INK)
    draw.arc([cx - 120, cy + 10, cx + 120, cy + 150], start=0, end=180, fill=RED, width=12)

    # Network/reputation visual motifs.
    nodes = [(420, 700), (620, 520), (1440, 560), (1620, 780), (500, 1120), (1550, 1120)]
    for a, b in zip(nodes, nodes[1:]):
        draw.line([a, b], fill=INK, width=8)
    for i, (x, y) in enumerate(nodes):
        draw.ellipse([x - 38, y - 38, x + 38, y + 38], fill=BG if i % 2 else RED, outline=INK, width=6)

    # Nameplate.
    draw.rectangle([120, 1370, CANVAS - 120, 1585], fill=INK)
    draw.text((155, 1415), title.upper(), font=title_font, fill=BG)

    y = 1640
    y = draw_wrapped(draw, one_liner, (150, y), 1750, body_font, fill=INK)
    y += 22
    y = draw_wrapped(draw, f"Vector: {vector}", (150, y), 1750, small_font, fill=INK)
    y = draw_wrapped(draw, f"System: {system}", (150, y), 1750, small_font, fill=INK)

    draw.text((150, CANVAS - 165), f"Hidden gag grid: {gag}", font=small_font, fill=RED)
    draw.text((CANVAS - 620, CANVAS - 165), "NO-COST MOCK RENDER", font=small_font, fill=RED)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", dpi=(DPI, DPI))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    manifest = load_json(Path(args.prompt))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log: list[dict[str, Any]] = []
    for card in manifest["cards"]:
        slug = card.get("slug") or card["title"].replace(" ", "_")
        out_path = out_dir / f"{card['card_id']}-{slug}.png"
        render_card(card, manifest.get("wave_title", "GPP"), out_path)
        log.append({
            "card_id": card["card_id"],
            "title": card["title"],
            "output_file": str(out_path),
            "renderer": "no_cost_mock",
            "width": CANVAS,
            "height": CANVAS,
            "dpi": DPI,
            "rendered_at_unix": int(time.time()),
        })
        print(f"Mock rendered {out_path}")

    (out_dir / "render_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
