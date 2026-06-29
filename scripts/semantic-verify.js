#!/usr/bin/env node
"use strict";

const fs = require("fs");
const crypto = require("crypto");
const { canonicalize } = require("json-canonicalize");

const manifestPath = process.env.MANIFEST_PATH || ".well-known/farcaster/manifest.json";
const canonicalPath = process.env.MANIFEST_JCS_PATH || ".well-known/farcaster/manifest.jcs";
const lockPath = process.env.MANIFEST_LOCK_PATH || ".well-known/farcaster/manifest.lock.json";

function fail(message) {
  console.error(`::error::${message}`);
  process.exit(1);
}

function must(condition, message) {
  if (!condition) fail(message);
}

function readJson(path) {
  try {
    return JSON.parse(fs.readFileSync(path, "utf8"));
  } catch (error) {
    fail(`Unable to read valid JSON at ${path}: ${error.message}`);
  }
}

function readText(path) {
  try {
    return fs.readFileSync(path, "utf8");
  } catch (error) {
    fail(`Unable to read ${path}: ${error.message}`);
  }
}

function isHttpsUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:";
  } catch (_) {
    return false;
  }
}

function assertNoEmptyStrings(value, path = "manifest") {
  if (typeof value === "string") {
    must(value.trim().length > 0, `${path} must not be an empty string`);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertNoEmptyStrings(item, `${path}[${index}]`));
    return;
  }
  if (value && typeof value === "object") {
    for (const [key, nested] of Object.entries(value)) {
      assertNoEmptyStrings(nested, `${path}.${key}`);
    }
  }
}

function canonicalizeOrFail(value) {
  try {
    return canonicalize(value);
  } catch (error) {
    fail(`RFC8785 canonicalization failed: ${error.message}`);
  }
}

const manifest = readJson(manifestPath);
const canonicalText = fs.existsSync(canonicalPath) ? readText(canonicalPath) : null;
const lock = fs.existsSync(lockPath) ? readJson(lockPath) : null;

assertNoEmptyStrings(manifest);

// Identity stability.
must(typeof manifest.id === "string" && /^[a-z0-9._-]+$/.test(manifest.id), "id must be stable lowercase [a-z0-9._-]");
must(manifest.id.length >= 3 && manifest.id.length <= 64, "id must be 3-64 characters");
must(typeof manifest.name === "string" && manifest.name.trim().length > 0, "name must be non-empty");

// Developer and app operational constraints.
must(manifest.developer && typeof manifest.developer === "object", "developer object is required");
must(typeof manifest.developer.name === "string" && manifest.developer.name.trim().length > 0, "developer.name must be non-empty");
must(typeof manifest.developer.url === "string" && isHttpsUrl(manifest.developer.url), "developer.url must be HTTPS");

if (manifest.website !== undefined) {
  must(typeof manifest.website === "string" && isHttpsUrl(manifest.website), "website must be HTTPS when present");
}

must(manifest.app && typeof manifest.app === "object", "app object is required");
must(typeof manifest.app.url === "string" && isHttpsUrl(manifest.app.url), "app.url must be HTTPS");
must(Array.isArray(manifest.app.permissions), "app.permissions must be an array");

const allowedPermissions = new Set(["farcaster.read", "farcaster.write"]);
for (const permission of manifest.app.permissions) {
  must(allowedPermissions.has(permission), `invalid permission: ${permission}`);
}

// Asset constraints.
must(typeof manifest.icon === "string" && isHttpsUrl(manifest.icon), "icon must be an HTTPS URL");
must(new URL(manifest.icon).pathname.toLowerCase().endsWith(".png"), "icon must be a PNG URL");

must(Array.isArray(manifest.screenshots), "screenshots must be an array");
must(manifest.screenshots.length >= 1, "at least one screenshot is required");
for (const screenshot of manifest.screenshots) {
  must(typeof screenshot === "string" && isHttpsUrl(screenshot), `screenshot must be HTTPS: ${screenshot}`);
  const path = new URL(screenshot).pathname.toLowerCase();
  must(path.endsWith(".png") || path.endsWith(".jpg") || path.endsWith(".jpeg") || path.endsWith(".webp"), `screenshot must be an image URL: ${screenshot}`);
}

// Canonical drift detection using RFC8785 JCS.
if (canonicalText !== null) {
  const derivedCanonical = canonicalizeOrFail(manifest);
  must(canonicalText === derivedCanonical, "manifest.json does not match manifest.jcs RFC8785 canonical bytes");
}

// Lock doctrine.
if (lock) {
  must(lock.authority === false, "lock authority must remain false");
  must(lock.canonicalization === "RFC8785", "lock canonicalization must be RFC8785");
  must(lock.manifest_path === canonicalPath, `lock manifest_path must be ${canonicalPath}`);
  must(lock.canonical_source === "manifest.jcs", "lock canonical_source must be manifest.jcs");

  if (lock.manifest_id) {
    must(lock.manifest_id === manifest.id, `manifest_id drift: lock=${lock.manifest_id} manifest=${manifest.id}`);
  }

  if (lock.created_at) {
    const createdAt = Date.parse(lock.created_at);
    must(!Number.isNaN(createdAt), "lock created_at must be ISO-8601");
    must(createdAt <= Date.now() + 60000, "lock created_at must not be future-dated");
  }

  if (canonicalText !== null && lock.sha256) {
    const actualHash = crypto.createHash("sha256").update(canonicalText).digest("hex");
    must(lock.sha256 === actualHash, `lock sha256 drift: lock=${lock.sha256} actual=${actualHash}`);
  }
}

console.log("Semantic verification doctrine v2 passed with RFC8785 canonicalization.");
