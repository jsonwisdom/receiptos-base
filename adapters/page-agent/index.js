const { sha256 } = require("./hash");

const RECEIPT_TYPE = "PAGE_AGENT_UI_ACTION_V0_1";

async function runVerifiedPageAction({ command, domBefore, execute, timestamp }) {
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

  return {
    type: RECEIPT_TYPE,
    command_hash: sha256(command),
    dom_before_hash: sha256(domBefore),
    dom_after_hash: sha256(result.domAfter),
    action_result: result.action_result || null,
    authority: false,
    timestamp: timestamp || new Date().toISOString()
  };
}

module.exports = { RECEIPT_TYPE, runVerifiedPageAction };
