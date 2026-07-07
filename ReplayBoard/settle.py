#!/usr/bin/env python3
"""ReplayBoard settle receipt runner.

Evidence-first resolution helper.

The runner fetches a public evidence URL, hashes the raw response bytes, evaluates
an explicit settle condition from a JSON manifest, and appends a receipt to a
JSONL ledger. It does not assert truth by authority; it records observed bytes,
headers, timestamps, and deterministic evaluation results.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Tuple

USER_AGENT = "ReceiptOS-ReplayBoard/1.0"
CANONICALIZER_VERSION = "REPLAYBOARD_SETTLE_V1"
GENESIS_PREV_RECEIPT_HASH = "sha256:" + "0" * 64


class SettleError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        raise SettleError("CANONICALIZATION_FAILURE floats_not_allowed")
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key).strip(): normalize(value[key]) for key in sorted(value)}
    raise SettleError(f"CANONICALIZATION_FAILURE unsupported_type={type(value).__name__}")


def canonical_json(value: Any) -> str:
    return json.dumps(normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def receipt_hash(receipt: Dict[str, Any]) -> str:
    basis = dict(receipt)
    basis["receipt_hash"] = None
    return sha256_bytes(canonical_json(basis).encode("utf-8"))


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SettleError("MANIFEST_MUST_BE_OBJECT")
    return data


def load_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SettleError(f"INVALID_LEDGER_JSONL line={line_number} error={exc}") from exc
    return rows


def atomic_append_jsonl(path: pathlib.Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(row) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def write_bytes(path: pathlib.Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def last_hash(rows: Iterable[Dict[str, Any]]) -> str:
    last = None
    for row in rows:
        last = row
    if not last:
        return GENESIS_PREV_RECEIPT_HASH
    value = last.get("receipt_hash")
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise SettleError("INVALID_PREV_RECEIPT_HASH")
    return value


def prior_resolution(rows: Iterable[Dict[str, Any]], claim_id: str) -> Optional[Any]:
    for row in rows:
        if row.get("claim_id") == claim_id and row.get("status") in {"RESOLVED", "ALREADY_RESOLVED"}:
            return row.get("resolution")
    return None


def fetch_evidence(url: str, timeout_seconds: int, etag: Optional[str], last_modified: Optional[str], raw_output_path: pathlib.Path) -> Dict[str, Any]:
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    request = urllib.request.Request(url, headers=headers, method="GET")
    fetched_at = utc_now()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read()
            write_bytes(raw_output_path, body)
            selected_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() in {"content-type", "etag", "last-modified", "cache-control"}
            }
            return {
                "requested_url": url,
                "final_url": response.geturl(),
                "fetched_at": fetched_at,
                "status_code": response.status,
                "headers": selected_headers,
                "content_hash": sha256_bytes(body),
                "body_size_bytes": len(body),
                "raw_artifact_path": str(raw_output_path),
                "hash_method": "sha256(raw_response_body_bytes)",
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        write_bytes(raw_output_path, body)
        selected_headers = {
            key: value
            for key, value in exc.headers.items()
            if key.lower() in {"content-type", "etag", "last-modified", "cache-control"}
        }
        return {
            "requested_url": url,
            "final_url": exc.geturl(),
            "fetched_at": fetched_at,
            "status_code": exc.code,
            "headers": selected_headers,
            "content_hash": sha256_bytes(body) if body else None,
            "body_size_bytes": len(body),
            "raw_artifact_path": str(raw_output_path),
            "hash_method": "sha256(raw_response_body_bytes)",
            "error": f"HTTP_ERROR:{exc.code}",
        }
    except Exception as exc:
        write_bytes(raw_output_path, b"")
        return {
            "requested_url": url,
            "final_url": url,
            "fetched_at": fetched_at,
            "status_code": None,
            "headers": {},
            "content_hash": None,
            "body_size_bytes": 0,
            "raw_artifact_path": str(raw_output_path),
            "hash_method": "sha256(raw_response_body_bytes)",
            "error": f"FETCH_ERROR:{type(exc).__name__}:{exc}",
        }


def evaluate(manifest: Dict[str, Any], evidence: Dict[str, Any]) -> Tuple[str, Optional[Any], str]:
    condition = manifest.get("settle_condition")
    if not isinstance(condition, dict):
        raise SettleError("SETTLE_CONDITION_MISSING")

    expected_status = condition.get("status_code", 200)
    expected_hash = condition.get("content_hash")
    resolution = condition.get("resolution")

    if evidence.get("error"):
        return "UNRESOLVED", None, str(evidence["error"])
    if evidence.get("status_code") != expected_status:
        return "UNRESOLVED", None, f"STATUS_MISMATCH expected={expected_status} got={evidence.get('status_code')}"
    if expected_hash and evidence.get("content_hash") != expected_hash:
        return "DISPUTED", None, f"HASH_MISMATCH expected={expected_hash} got={evidence.get('content_hash')}"
    if resolution is None:
        return "UNRESOLVED", None, "RESOLUTION_MISSING"
    return "RESOLVED", resolution, "SETTLE_CONDITION_MATCHED"


def make_receipt(manifest: Dict[str, Any], ledger: pathlib.Path, raw_output_path: pathlib.Path) -> Dict[str, Any]:
    claim_id = manifest.get("claim_id")
    condition = manifest.get("settle_condition")
    if not isinstance(claim_id, str) or not claim_id:
        raise SettleError("CLAIM_ID_MISSING")
    if not isinstance(condition, dict) or not isinstance(condition.get("url"), str):
        raise SettleError("SETTLE_CONDITION_URL_MISSING")

    rows = load_jsonl(ledger)
    prev_receipt_hash = last_hash(rows)
    previous = prior_resolution(rows, claim_id)

    evidence = fetch_evidence(
        condition["url"],
        int(manifest.get("timeout_seconds", 20)),
        condition.get("etag"),
        condition.get("last_modified"),
        raw_output_path,
    )
    status, resolution, reason = evaluate(manifest, evidence)

    if previous is not None:
        if status == "RESOLVED" and previous == resolution:
            status = "ALREADY_RESOLVED"
            reason = "IDEMPOTENT_NO_OP"
        elif status == "RESOLVED" and previous != resolution:
            status = "DISPUTED"
            reason = f"CONFLICTING_RESOLUTION prior={previous} attempted={resolution}"
            resolution = None

    receipt: Dict[str, Any] = {
        "canonicalizer_version": CANONICALIZER_VERSION,
        "claim_id": claim_id,
        "created_at": utc_now(),
        "evidence": evidence,
        "invariants": {
            "authority": False,
            "fail_closed": True,
            "replayable": True,
            "truth_claim": False,
            "witness_only": True,
        },
        "ledger_path": str(ledger),
        "prev_receipt_hash": prev_receipt_hash,
        "reason": reason,
        "receipt_hash": None,
        "resolution": resolution,
        "settle_condition_url": condition["url"],
        "status": status,
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="ReplayBoard settle receipt runner")
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--ledger", required=True, type=pathlib.Path)
    parser.add_argument("--raw-output", default="/tmp/replayboard-evidence/evidence.bin", type=pathlib.Path)
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()

    receipt = make_receipt(load_json(args.manifest), args.ledger, args.raw_output)
    atomic_append_jsonl(args.ledger, receipt)

    if args.print:
        print(canonical_json(receipt))
    else:
        print(f"REPLAYBOARD_SETTLE_STATUS={receipt['status']}")
        print(f"REPLAYBOARD_RECEIPT_HASH={receipt['receipt_hash']}")
        print(f"REPLAYBOARD_CLAIM_ID={receipt['claim_id']}")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"settle_status={receipt['status']}\n")
            handle.write(f"receipt_hash={receipt['receipt_hash']}\n")
            handle.write(f"claim_id={receipt['claim_id']}\n")

    return 0 if receipt["status"] in {"RESOLVED", "ALREADY_RESOLVED", "UNRESOLVED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
