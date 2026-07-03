const { sha256 } = require("./hash");
const { RECEIPT_TYPE } = require("./index");

const WIRE_EVENT_TYPE = "receiptos.wire.page_agent.ui_action.v0_1";
const WIRE_EVENT_VERSION = "0.1.0";

function toWireEvent({ receipt, command, domBefore, source = "page-agent-adapter", sequence = 0 }) {
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
  if (receipt.command_hash !== sha256(command)) {
    throw new Error("command hash mismatch");
  }
  if (receipt.dom_before_hash !== sha256(domBefore)) {
    throw new Error("DOM before hash mismatch");
  }
  if (!receipt.dom_after_hash || typeof receipt.dom_after_hash !== "string") {
    throw new Error("DOM after hash missing");
  }

  const payload = {
    receipt_type: receipt.type,
    command_hash: receipt.command_hash,
    dom_before_hash: receipt.dom_before_hash,
    dom_after_hash: receipt.dom_after_hash,
    action_result_hash: sha256(JSON.stringify(receipt.action_result || null)),
    replay_required: true,
    authority: false
  };

  return {
    type: WIRE_EVENT_TYPE,
    version: WIRE_EVENT_VERSION,
    source,
    sequence,
    timestamp: receipt.timestamp,
    payload,
    payload_hash: sha256(JSON.stringify(payload)),
    authority: false,
    witness_only: true,
    side_effect: false
  };
}

function verifyWireEventSchema(event) {
  const required = [
    "type",
    "version",
    "source",
    "sequence",
    "timestamp",
    "payload",
    "payload_hash",
    "authority",
    "witness_only",
    "side_effect"
  ];

  for (const key of required) {
    if (!(key in event)) {
      return { ok: false, reason: `missing ${key}` };
    }
  }

  if (event.type !== WIRE_EVENT_TYPE) return { ok: false, reason: "wrong event type" };
  if (event.authority !== false) return { ok: false, reason: "authority drift" };
  if (event.witness_only !== true) return { ok: false, reason: "witness_only drift" };
  if (event.side_effect !== false) return { ok: false, reason: "side effect drift" };
  if (event.payload.authority !== false) return { ok: false, reason: "payload authority drift" };
  if (event.payload.replay_required !== true) return { ok: false, reason: "replay flag drift" };
  if (sha256(JSON.stringify(event.payload)) !== event.payload_hash) {
    return { ok: false, reason: "payload hash mismatch" };
  }

  return { ok: true };
}

module.exports = {
  WIRE_EVENT_TYPE,
  WIRE_EVENT_VERSION,
  toWireEvent,
  verifyWireEventSchema
};
