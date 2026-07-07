const { canonicalize: jcsCanonicalize } = require("json-canonicalize");
const { createHash } = require("node:crypto");

function canonicalJSON(value) {
  return jcsCanonicalize(value);
}

function sha256Hex(value) {
  return createHash("sha256").update(value).digest("hex");
}

function hashCanonical(value) {
  return sha256Hex(canonicalJSON(value));
}

function receiptIdFromCore(core) {
  return `ros-${hashCanonical(core)}`;
}

module.exports = {
  canonicalJSON,
  sha256Hex,
  hashCanonical,
  receiptIdFromCore,
};
