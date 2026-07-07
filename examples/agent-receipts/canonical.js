"use strict";

const crypto = require("crypto");

function canonicalize(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(canonicalize).join(",")}]`;
  }
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`).join(",")}}`;
}

function sha256Hex(value) {
  const bytes = typeof value === "string" ? value : canonicalize(value);
  return crypto.createHash("sha256").update(bytes, "utf8").digest("hex");
}

function sha256Ref(value) {
  return `sha256:${sha256Hex(value)}`;
}

module.exports = {
  canonicalize,
  sha256Hex,
  sha256Ref,
};
