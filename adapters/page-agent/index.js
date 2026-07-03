const { sha256 } = require("./hash");

const RECEIPT_TYPE = "PAGE_AGENT_UI_ACTION_V0_1";

async function runVerifiedPageAction({ command, domBefore, execute, timestamp, timestampMs }) {
  if (!command || typeof command !== "string") {
    throw new Error("command must be a non-empty string");
  }
  if (typeof domBefore !== "string") {
    throw new Error("domBefore must be a string");
  }
  if (typeof execute !== "function") {
    throw new Error("execute must be a function");
  }

  const result = await execute({ command, dom: domBefore });
  if (!result || typeof result.domAfter !== "string") {
    throw new Error("execute must return { domAfter }");
  }

  const emittedAtMs = timestampMs || Date.now();

  return {
    type: RECEIPT_TYPE,
    command_hash: sha256(command),
    dom_before_hash: sha256(domBefore),
    dom_after_hash: sha256(result.domAfter),
    action_result: result.action_result || null,
    authority: false,
    timestamp: timestamp || new Date(emittedAtMs).toISOString(),
    timestamp_ms: emittedAtMs
  };
}

async function emitPageAgentWireEvent({ command, domBefore, execute, recipient, timestampMs }) {
  const receipt = await runVerifiedPageAction({ command, domBefore, execute, timestampMs });
  const { toWireEvent } = require("./wire-event");

  return {
    receipt,
    wire_event: toWireEvent({ receipt, command, domBefore, recipient })
  };
}

module.exports = { RECEIPT_TYPE, runVerifiedPageAction, emitPageAgentWireEvent };
