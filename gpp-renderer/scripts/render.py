#!/usr/bin/env python3
"""Render a GPP wave prompt manifest through Replicate."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import replicate

DEFAULT_MODEL = ""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(manifest: dict[str, Any], card: dict[str, Any]) -> str:
    parts = [
        manifest.get("style_preamble", ""),
        f"Card title: {card['title']}.",
        f"Concept vector: {card.get('vector', '')}.",
        f"System: {card.get('system', '')}.",
        f"One-liner: {card.get('one_liner', '')}.",
        card["prompt"],
        "Keep text minimal and large; prioritize image composition over tiny readable typography.",
    ]
    return " ".join(part.strip() for part in parts if part)


def normalize_outputs(output: Any) -> list[str]:
    if output is None:
        return []
    if isinstance(output, str):
        return [output]
    if isinstance(output, list):
        return [str(item) for item in output]
    return [str(output)]


def is_flux_schnell(model: str) -> bool:
    return "flux-schnell" in model.lower()


def build_input_payload(model: str, prompt: str, negative_prompt: str, defaults: dict[str, Any]) -> dict[str, Any]:
    if is_flux_schnell(model):
        payload: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "output_quality": 95,
            "num_outputs": int(defaults.get("num_outputs") or 1),
        }
        steps = defaults.get("num_inference_steps")
        if steps is not None:
            payload["num_inference_steps"] = min(int(steps), 4)
        seed = defaults.get("seed")
        if seed is not None:
            payload["seed"] = seed
        return payload

    payload = {"prompt": prompt}
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    for key in ["width", "height", "num_outputs", "guidance_scale", "num_inference_steps", "seed"]:
        value = defaults.get(key)
        if value is not None:
            payload[key] = value
    return payload


def render_card(model: str, prompt: str, negative_prompt: str, defaults: dict[str, Any]) -> list[str]:
    input_payload = build_input_payload(model, prompt, negative_prompt, defaults)
    output = replicate.run(model, input=input_payload)
    return normalize_outputs(output)


def resolve_model(cli_model: str | None) -> str:
    model = (cli_model or os.getenv("REPLICATE_MODEL") or DEFAULT_MODEL).strip()
    if not model:
        raise RuntimeError("Missing production model. Set REPLICATE_MODEL or pass --model.")
    return model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, help="Path to wave prompt JSON")
    parser.add_argument("--out", required=True, help="Output directory for PNG files")
    parser.add_argument("--model", default=None)
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to pause between cards")
    args = parser.parse_args()

    if not os.getenv("REPLICATE_API_TOKEN"):
        raise RuntimeError("Missing REPLICATE_API_TOKEN environment variable")

    model = resolve_model(args.model)
    prompt_path = Path(args.prompt)
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(prompt_path)
    defaults = manifest.get("render_defaults", {})
    negative_prompt = manifest.get("negative_prompt", "")

    render_log: list[dict[str, Any]] = []

    for card in manifest["cards"]:
        card_id = card["card_id"]
        slug = card.get("slug") or card["title"].replace(" ", "_")
        filename = f"{card_id}-{slug}.png"
        out_path = output_dir / filename

        print(f"Rendering {card_id} — {card['title']}")
        prompt = build_prompt(manifest, card)
        urls = render_card(model, prompt, negative_prompt, defaults)
        if not urls:
            raise RuntimeError(f"No output returned for {card_id}")

        urlretrieve(urls[0], out_path)

        render_log.append(
            {
                "card_id": card_id,
                "title": card["title"],
                "slug": slug,
                "model": model,
                "output_file": str(out_path),
                "source_url_present": bool(urls[0]),
                "rendered_at_unix": int(time.time()),
            }
        )
        time.sleep(args.sleep)

    log_path = output_dir / "render_log.json"
    log_path.write_text(json.dumps(render_log, indent=2), encoding="utf-8")
    print(f"Render log written to {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
