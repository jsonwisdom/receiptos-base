#!/usr/bin/env node
"use strict";

const fs = require("fs");
const crypto = require("crypto");

const manifestPath = process.env.MANIFEST_JCS_PATH || ".well-known/farcaster/manifest.jcs";
const lockPath = process.env.MANIFEST_LOCK_PATH || ".well-known/farcaster/manifest.lock.json";

function fail(message) {
  console.error(`::error::${message}`);
  process.exit(1);
}

function readJson(path) {
  try {
    return JSON.parse(fs.readFileSync(path, "utf8"));
  } catch (error) {
    fail(`Unable to read valid JSON at ${path}: ${error.message}`);
  }
}

if (!fs.existsSync(manifestPath)) {
  fail(`Canonical manifest missing at ${manifestPath}`);
}

if (!fs.existsSync(lockPath)) {
  fail(`Manifest lock missing at ${lockPath}`);
}

const canonicalBytes = fs.readFileSync(manifestPath);
const actualHash = crypto.createHash("sha256").update(canonicalBytes).digest("hex");
const lock = readJson(lockPath);

if (lock.canonicalization !== "RFC8785") {
  fail(`manifest.lock.json canonicalization must be RFC8785, got ${lock.canonicalization}`);
}

if (lock.authority !== false) {
  fail("manifest.lock.json must declare authority=false");
}

if (!/^[a-f0-9]{64}$/.test(lock.sha256 || "")) {
  fail("manifest.lock.json sha256 must be a lowercase 64-character hex digest");
}

if (lock.manifest_path && lock.manifest_path !== manifestPath) {
  fail(`manifest.lock.json manifest_path drift: expected ${manifestPath}, got ${lock.manifest_path}`);
}

if (lock.sha256 !== actualHash) {
  fail(`Manifest lock hash mismatch\nExpected: ${lock.sha256}\nActual:   ${actualHash}`);
}

if (lock.created_at) {
  const createdAt = Date.parse(lock.created_at);
  if (Number.isNaN(createdAt)) {
    fail("manifest.lock.json created_at must be an ISO-8601 timestamp");
  }
  if (createdAt > Date.now() + 60_000) {
    fail("manifest.lock.json created_at is future-dated");
  }
}

console.log("Manifest lock verification passed.");
console.log(`sha256=${actualHash}`);
