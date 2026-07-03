const { createHash } = require("node:crypto");

function sha256(input) {
  return createHash("sha256").update(String(input), "utf8").digest("hex");
}

module.exports = { sha256 };
