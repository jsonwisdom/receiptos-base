const { createHash } = require("node:crypto");

const HASH_ALGORITHM = "sha256";

function sha256(input) {
  return createHash("sha256").update(String(input), "utf8").digest("hex");
}

function canonicalJson(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(",")}]`;
  }

  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
}

function hashCanonicalJson(value) {
  return sha256(canonicalJson(value));
}

module.exports = { HASH_ALGORITHM, sha256, canonicalJson, hashCanonicalJson };
