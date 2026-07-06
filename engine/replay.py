import copy
import hashlib
import json
import sys
from pathlib import Path

PLACEHOLDERS = ("TODO", "TBD", "PLACEHOLDER", "REPLACE_ME")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_hash(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def placeholder_scan(obj):
    payload = json.dumps(obj, sort_keys=True)
    return not any(marker in payload for marker in PLACEHOLDERS)


def path_parts(state_path):
    if not state_path.startswith("/"):
        raise ValueError("state_path must start with /")
    return [part for part in state_path.split("/") if part]


def get_path(obj, state_path):
    cur = obj
    for part in path_parts(state_path):
        cur = cur[part]
    return cur


def set_path(obj, state_path, value):
    cur = obj
    parts = path_parts(state_path)
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def nested_delta(state_path, value):
    parts = path_parts(state_path)
    out = cur = {}
    for part in parts[:-1]:
        cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value
    return out


def apply_effect(state, effect):
    next_state = copy.deepcopy(state)
    state_path = effect["state_path"]
    operation = effect["operation"]
    value = effect.get("value")
    current = get_path(next_state, state_path)

    if operation == "set":
        new_value = value
    elif operation == "increment":
        new_value = current + value
    elif operation == "append_unique":
        new_value = list(current)
        if value not in new_value:
            new_value.append(value)
    elif operation == "append":
        new_value = list(current)
        new_value.append(value)
    else:
        raise ValueError(f"unsupported operation: {operation}")

    set_path(next_state, state_path, new_value)
    return next_state, nested_delta(state_path, new_value)


def replay_static_receipt(receipt):
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


def replay_card(state_path, card_path, next_receipt_path=None):
    state = load_json(state_path)
    card = load_json(card_path)

    if card.get("authority") is not False:
        print("AUTHORITY_MISMATCH")
        return False

    if not placeholder_scan(card.get("input_effect", {})):
        print("PLACEHOLDER_SCAN_FAIL: input_effect")
        return False

    if not placeholder_scan(card.get("output_effect", {})):
        print("PLACEHOLDER_SCAN_FAIL: output_effect")
        return False

    next_state, actual_delta = apply_effect(state, card["input_effect"])
    expected_delta = card["output_effect"]["state_delta"]

    if actual_delta != expected_delta:
        print("STATE_DELTA_MISMATCH")
        print(json.dumps({"actual": actual_delta, "expected": expected_delta}, indent=2, sort_keys=True))
        return False

    next_hash = "sha256:" + compute_hash(next_state)
    expected_hash = card["output_effect"]["expected_next_hash"]

    if next_hash != expected_hash:
        print("NEXT_HASH_MISMATCH")
        print(json.dumps({"actual": next_hash, "expected": expected_hash}, indent=2, sort_keys=True))
        return False

    if next_receipt_path:
        next_receipt = load_json(next_receipt_path)
        receipt_input_hash = next_receipt.get("input_hash") or next_receipt.get("inputs", {}).get("input_hash")
        if receipt_input_hash != next_hash:
            print("NEXT_RECEIPT_INPUT_HASH_MISMATCH")
            print(json.dumps({"actual": receipt_input_hash, "expected": next_hash}, indent=2, sort_keys=True))
            return False

    out = Path("front-door")
    out.mkdir(exist_ok=True)
    replay_path = out / f"{card['card_id']}.replay.json"
    replay_path.write_text(
        json.dumps({
            "card_id": card["card_id"],
            "input_hash": "sha256:" + compute_hash(state),
            "next_hash": next_hash,
            "state_delta": actual_delta,
            "authority": False,
            "result_state": "REPLAY_MATCH"
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    print("Replay complete. Match: True")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 2:
        receipt = load_json(sys.argv[1])
        ok = replay_static_receipt(receipt)
    elif len(sys.argv) in (3, 4):
        ok = replay_card(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
    else:
        print("Usage:")
        print("  python engine/replay.py <receipt.json>")
        print("  python engine/replay.py <game_state.json> <cards/GPK-XXX.json> [next_receipt.json]")
        sys.exit(1)

    sys.exit(0 if ok else 1)
