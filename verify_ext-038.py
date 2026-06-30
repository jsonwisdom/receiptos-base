#!/usr/bin/env python3
import json
import hashlib
import sys
from pathlib import Path

SPEC = "market/ext-038-operational-alerts.json"
ALERT_OUTPUT = "receipts/tntr-020-operational-alerts.json"
FORBIDDEN = {"TRUE", "FALSE", "YES", "NO", "RESOLVED", "GUILTY", "PROVEN", "VERDICT", "TRIBUNAL"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def add_alert(alerts, cls, path, detail):
    alerts.append({
        "class": cls,
        "path": path,
        "detail": detail,
        "severity": "critical",
        "action": "signal_only",
        "authority": False
    })


def scan_forbidden(obj, path, alerts):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan_forbidden(v, f"{path}.{k}", alerts)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            scan_forbidden(item, f"{path}[{i}]", alerts)
    elif isinstance(obj, str) and obj.upper() in FORBIDDEN:
        add_alert(alerts, "forbidden_semantics_drift", path, f"forbidden token: {obj}")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recompute_stack_hash(paths):
    h = hashlib.sha256()
    for path in sorted(paths):
        p = Path(path)
        if p.exists():
            h.update(path.encode("utf-8"))
            h.update(b"\0")
            h.update(sha256_file(path).encode("utf-8"))
            h.update(b"\n")
    return "0x" + h.hexdigest()


def main():
    print("EXT-038 operational alerts")
    alerts = []

    if not Path(SPEC).exists():
        add_alert(alerts, "receipt_drift", SPEC, "missing alert spec")
    else:
        spec = load_json(SPEC)
        if spec.get("authority") is not False:
            add_alert(alerts, "authority_drift", SPEC, "spec authority is not false")
        if spec.get("resolution_semantics") != "absent":
            add_alert(alerts, "resolution_semantics_drift", SPEC, "spec resolution semantics not absent")
        if spec.get("mode") != "signal_only":
            add_alert(alerts, "receipt_drift", SPEC, "alert mode is not signal_only")
        scan_forbidden(spec, SPEC, alerts)

        watched = spec.get("watched_artifacts", [])
        required_verifiers = spec.get("required_verifiers", [])

        for path in watched:
            p = Path(path)
            if not p.exists():
                add_alert(alerts, "receipt_drift", path, "missing watched artifact")
                continue
            try:
                data = load_json(path)
            except Exception as exc:
                add_alert(alerts, "receipt_drift", path, f"invalid json: {exc}")
                continue
            scan_forbidden(data, path, alerts)
            if isinstance(data, dict):
                if "authority" in data and data.get("authority") is not False:
                    add_alert(alerts, "authority_drift", path, "authority is not false")
                if "resolution_semantics" in data and data.get("resolution_semantics") != "absent":
                    add_alert(alerts, "resolution_semantics_drift", path, "resolution semantics not absent")
                if path.startswith("receipts/") and data.get("status") not in ("executed", "PRODUCTION"):
                    add_alert(alerts, "receipt_drift", path, "receipt status is not executed or production")

        for path in required_verifiers:
            if not Path(path).exists():
                add_alert(alerts, "receipt_drift", path, "missing verifier")

        manifest_path = spec.get("production_manifest")
        if manifest_path and Path(manifest_path).exists():
            manifest = load_json(manifest_path)
            expected = manifest.get("stack_hash")
            hash_inputs = manifest.get("stack_hash_inputs", watched)
            actual = recompute_stack_hash(hash_inputs)
            if expected != actual:
                add_alert(alerts, "hash_mismatch", manifest_path, f"expected {expected}, recomputed {actual}")

    output = {
        "receipt_id": "TNTR-020-OPERATIONAL-ALERTS",
        "issue": "EXT-038",
        "gate": "Operational Alerts",
        "status": "clean" if not alerts else "drift_detected",
        "authority": False,
        "resolution_semantics": "absent",
        "mode": "signal_only",
        "alerts": alerts
    }
    Path("receipts").mkdir(exist_ok=True)
    Path(ALERT_OUTPUT).write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "alert_count": len(alerts)}, indent=2))
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
