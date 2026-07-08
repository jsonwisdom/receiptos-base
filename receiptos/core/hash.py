import copy
import hashlib
import json
import unicodedata


HASH_PREFIX = "sha256:"

EXCLUDED_TOP_LEVEL_FIELDS = {
    "receipt_id",
    "core_hash",
    "hashes",
    "variants",
    "approval_status",
    "publish_targets",
    "replay_status",
    "created_at",
    "updated_at",
    "previous_receipt",
    "cid",
}


def _normalize_nfc(value):
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalize_nfc(item) for item in value]
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", str(key)): _normalize_nfc(item)
            for key, item in value.items()
        }
    return value


def receipt_core(card):
    """Return the immutable hash core for a ReceiptOS card packet."""
    core = copy.deepcopy(card)

    for field in EXCLUDED_TOP_LEVEL_FIELDS:
        core.pop(field, None)

    birth_witness = core.get("birth_witness")
    if isinstance(birth_witness, dict):
        birth_witness.pop("witness_hash", None)

    custody = core.get("custody")
    if isinstance(custody, dict):
        custody.pop("chain_head", None)

    return _normalize_nfc(core)


def canonical_json(value):
    """Serialize using the ReceiptOS restricted canonical JSON profile."""
    return json.dumps(
        _normalize_nfc(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def canonical_receipt_hash(card):
    """Compute sha256 over canonical JSON for the immutable receipt core."""
    payload = canonical_json(receipt_core(card)).encode("utf-8")
    return HASH_PREFIX + hashlib.sha256(payload).hexdigest()
