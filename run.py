#!/usr/bin/env python3
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

URLS = {
    "eo14409": "https://www.whitehouse.gov/presidential-actions/2026/06/promoting-advanced-artificial-intelligence-innovation-and-security/"
}

p = argparse.ArgumentParser()
p.add_argument("command", choices=["collect"])
p.add_argument("--source", required=True, choices=URLS)
p.add_argument("--as-of", required=True)
a = p.parse_args()

req = Request(URLS[a.source], headers={"User-Agent": "BlackBookOfEyes/0.1"})
with urlopen(req, timeout=30) as response:
    raw = response.read()
    status = response.status

raw_hash = hashlib.sha256(raw).hexdigest()
raw_dir = Path("/app/work/raw") / a.source
raw_dir.mkdir(parents=True, exist_ok=True)
raw_path = raw_dir / f"{raw_hash}.bin"

if not raw_path.exists():
    raw_path.write_bytes(raw)

receipt = {
    "schema_version": "0.1-smoke",
    "source_id": a.source,
    "source_url": URLS[a.source],
    "as_of": a.as_of,
    "retrieved_at": datetime.now(timezone.utc).isoformat(),
    "http_status": status,
    "raw_sha256": raw_hash,
    "raw_bytes": len(raw),
    "parent_receipt_hash": None,
    "parent_kind": "GENESIS"
}

canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
receipt_hash = hashlib.sha256(canonical).hexdigest()
receipt["receipt_hash"] = receipt_hash

receipt_dir = Path("/app/out/receipts")
receipt_dir.mkdir(parents=True, exist_ok=True)
(receipt_dir / f"{receipt_hash}.json").write_text(
    json.dumps(receipt, sort_keys=True, indent=2) + "\n"
)

print(json.dumps(receipt, indent=2))
