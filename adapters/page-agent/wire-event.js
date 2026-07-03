const { HASH_ALGORITHM, canonicalJson, hashCanonicalJson, sha256 } = require("./hash");
const { RECEIPT_TYPE } = require("./index");

const WIRE_EVENT_TYPE = "receiptos.wire.page_agent.ui_action.v0_1";
const WIRE_EVENT_VERSION = "0.1.0";
const DEFAULT_RECIPIENT = "jaywisdom.base.eth";

function asBytes32(hash) {
  if (typeof hash !== "string") throw new Error("hash must be a string");
  const normalized = hash.startsWith("0x") ? hash : `0x${hash}`;
  if (!/^0x[0-9a-f]{64}$/i.test(normalized)) {
    throw new Error("hash must be bytes32 hex");
  }
  return normalized.toLowerCase();
}

function hashBytes32(input) {
  return asBytes32(sha256(input));
}

function canonicalHashBytes32(value) {
  return asBytes32(hashCanonicalJson(value));
}

function attachOptionalExtensions(event, extensions = {}) {
  const next = { ...event };

  if (extensions.eas_schema_uid !== undefined) {
    next.eas_schema_uid = extensions.eas_schema_uid;
  }
  if (extensions.replay_engine_version !== undefined) {
    next.replay_engine_version = extensions.replay_engine_version;
  }
  if (extensions.prev_receipt_hash !== undefined) {
    next.prev_receipt_hash = asBytes32(extensions.prev_receipt_hash);
  }

  return next;
}

function createPageAgentWireEvent({
  payload,
  domBefore,
  domAfter,
  command,
  timestamp = Date.now(),
  recipient = DEFAULT_RECIPIENT,
  extensions = {}
}) {
  if (!payload || typeof payload !== "object") {
    throw new Error("payload is required");
  }
  if (!command || typeof command !== "string") {
    throw new Error("command must be a non-empty string");
  }
  if (typeof domBefore !== "string") {
    throw new Error("domBefore must be a string");
  }
  if (typeof domAfter !== "string") {
    throw new Error("domAfter must be a string");
  }
  if (!Number.isSafeInteger(timestamp) || timestamp <= 0) {
    throw new Error("timestamp must be a positive Unix ms integer");
  }

  return attachOptionalExtensions({
    event_type: WIRE_EVENT_TYPE,
    version: WIRE_EVENT_VERSION,
    timestamp,
    recipient,
    replay_required: true,
    authority: false,
    hash_algorithm: HASH_ALGORITHM,
    payload_hash: canonicalHashBytes32(payload),
    command_hash: hashBytes32(command),
    dom_before_hash: hashBytes32(domBefore),
    dom_after_hash: hashBytes32(domAfter),
    receipt_type: RECEIPT_TYPE
  }, extensions);
}

function toWireEvent({ receipt, command, domBefore, recipient = DEFAULT_RECIPIENT, extensions = {} }) {
  if (!receipt || typeof receipt !== "object") {
    throw new Error("receipt is required");
  }
  if (!command || typeof command !== "string") {
    throw new Error("command must be a non-empty string");
  }
  if (typeof domBefore !== "string") {
    throw new Error("domBefore must be a string");
  }
  if (receipt.type !== RECEIPT_TYPE) {
    throw new Error("unsupported receipt type");
  }
  if (receipt.authority !== false) {
    throw new Error("authority drift");
  }
  if (asBytes32(receipt.command_hash) !== hashBytes32(command)) {
    throw new Error("command hash mismatch");
  }
  if (asBytes32(receipt.dom_before_hash) !== hashBytes32(domBefore)) {
    throw new Error("DOM before hash mismatch");
  }
  if (!receipt.dom_after_hash || typeof receipt.dom_after_hash !== "string") {
    throw new Error("DOM after hash missing");
  }

  const timestamp = typeof receipt.timestamp_ms === "number"
    ? receipt.timestamp_ms
    : Date.parse(receipt.timestamp);

  return attachOptionalExtensions({
    event_type: WIRE_EVENT_TYPE,
    version: WIRE_EVENT_VERSION,
    timestamp,
    recipient,
    replay_required: true,
    authority: false,
    hash_algorithm: HASH_ALGORITHM,
    payload_hash: canonicalHashBytes32(receipt.action_result || null),
    command_hash: asBytes32(receipt.command_hash),
    dom_before_hash: asBytes32(receipt.dom_before_hash),
    dom_after_hash: asBytes32(receipt.dom_after_hash),
    receipt_type: receipt.type
  }, extensions);
}

function verifyWireEventSchema(event) {
  const required = [
    "event_type",
    "version",
    "timestamp",
    "recipient",
    "replay_required",
    "authority",
    "hash_algorithm",
    "payload_hash",
    "command_hash",
    "dom_before_hash",
    "dom_after_hash",
    "receipt_type"
  ];

  for (const key of required) {
    if (!(key in event)) {
      return { ok: false, reason: `missing ${key}` };
    }
  }

  if (event.event_type !== WIRE_EVENT_TYPE) return { ok: false, reason: "wrong event type" };
  if (event.version !== WIRE_EVENT_VERSION) return { ok: false, reason: "wrong version" };
  if (!Number.isSafeInteger(event.timestamp) || event.timestamp <= 0) {
    return { ok: false, reason: "invalid timestamp" };
  }
  if (event.authority !== false) return { ok: false, reason: "authority drift" };
  if (event.replay_required !== true) return { ok: false, reason: "replay flag drift" };
  if (event.hash_algorithm !== HASH_ALGORITHM) return { ok: false, reason: "hash algorithm drift" };
  if (event.receipt_type !== RECEIPT_TYPE) return { ok: false, reason: "wrong receipt type" };

  for (const key of ["payload_hash", "command_hash", "dom_before_hash", "dom_after_hash"]) {
    try {
      asBytes32(event[key]);
    } catch (_error) {
      return { ok: false, reason: `${key} invalid` };
    }
  }

  if (event.prev_receipt_hash !== undefined) {
    try {
      asBytes32(event.prev_receipt_hash);
    } catch (_error) {
      return { ok: false, reason: "prev_receipt_hash invalid" };
    }
  }

  return { ok: true };
}

module.exports = {
  WIRE_EVENT_TYPE,
  WIRE_EVENT_VERSION,
  DEFAULT_RECIPIENT,
  asBytes32,
  canonicalJson,
  canonicalHashBytes32,
  hashBytes32,
  createPageAgentWireEvent,
  toWireEvent,
  verifyWireEventSchema
};
