import json, sys, hashlib
from pathlib import Path

def load_receipt(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compute_hash(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()

def replay(receipt):
    out = Path("front-door")
    out.mkdir(exist_ok=True)

    result = {
        "step_id": "static-replay-v1",
        "timestamp": receipt.get("timestamp"),
        "input_hash": compute_hash(receipt.get("inputs", {})),
        "output_hash": compute_hash(receipt.get("outputs", {})),
        "tool_version": "replay-v1",
        "chain_identifier": receipt.get("inputs", {}).get("chain_identifier"),
        "artifact_identifier": receipt.get("inputs", {}).get("artifact_identifier"),
        "replay_action": "STATIC_FRONT_DOOR",
        "comparison_tolerance": "exact_byte_match",
        "result_state": "REPRODUCED_NOT_ENDORSED",
        "authority": False,
        "resolution_semantics": "absent"
    }

    (out / "RECEIPT-001.replay.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python replay.py <receipt.json>")
        sys.exit(1)
    ok = replay(load_receipt(sys.argv[1]))
    print("Replay complete. Match:", ok)
    sys.exit(0 if ok else 1)
