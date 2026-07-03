const { sha256 } = require("./hash");

function verifyReceiptSchema(receipt) {
  const required = [
    "type",
    "command_hash",
    "dom_before_hash",
    "dom_after_hash",
    "authority",
    "timestamp"
  ];

  for (const key of required) {
    if (!(key in receipt)) {
      return { ok: false, reason: `missing ${key}` };
    }
  }

  if (receipt.authority !== false) {
    return { ok: false, reason: "authority drift" };
  }

  return { ok: true };
}

async function verifyReplayParity({ command, domBefore, receipt, replay }) {
  const schema = verifyReceiptSchema(receipt);
  if (!schema.ok) return schema;

  if (sha256(command) !== receipt.command_hash) {
    return { ok: false, reason: "command hash mismatch" };
  }

  if (sha256(domBefore) !== receipt.dom_before_hash) {
    return { ok: false, reason: "DOM before hash mismatch" };
  }

  const replayResult = await replay({ command, dom: domBefore });
  if (!replayResult || typeof replayResult.domAfter !== "string") {
    return { ok: false, reason: "invalid replay result" };
  }

  if (sha256(replayResult.domAfter) !== receipt.dom_after_hash) {
    return { ok: false, reason: "DOM after hash mismatch" };
  }

  return { ok: true };
}

module.exports = { verifyReceiptSchema, verifyReplayParity };
