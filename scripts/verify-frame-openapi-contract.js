#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const surface = require('../frame/ext-099-frame-capability-surface');

const specPath = path.join(__dirname, '..', 'openapi', 'ext-101-frame-readonly-openapi.json');
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));

function fail(message, details = {}) {
  const error = new Error(message);
  error.details = details;
  throw error;
}

function getRef(ref) {
  const parts = ref.replace(/^#\//, '').split('/');
  let node = spec;
  for (const part of parts) node = node[part];
  return node;
}

function validateConst(value, expected, pathName) {
  if (value !== expected) fail(`const mismatch at ${pathName}`, { value, expected });
}

function validateType(value, type, pathName) {
  const allowed = Array.isArray(type) ? type : [type];
  const actual = value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;
  if (!allowed.includes(actual)) fail(`type mismatch at ${pathName}`, { actual, allowed });
}

function validateSchema(value, schema, pathName = '$') {
  if (!schema) return;
  if (schema.$ref) return validateSchema(value, getRef(schema.$ref), pathName);
  if (schema.allOf) {
    for (const child of schema.allOf) validateSchema(value, child, pathName);
    return;
  }
  if (schema.const !== undefined) validateConst(value, schema.const, pathName);
  if (schema.enum && !schema.enum.includes(value)) fail(`enum mismatch at ${pathName}`, { value, enum: schema.enum });
  if (schema.type) validateType(value, schema.type, pathName);
  if (schema.required) {
    for (const key of schema.required) {
      if (!Object.prototype.hasOwnProperty.call(value, key)) fail(`missing required field at ${pathName}.${key}`);
    }
  }
  if (schema.properties && value && typeof value === 'object' && !Array.isArray(value)) {
    for (const [key, child] of Object.entries(schema.properties)) {
      if (Object.prototype.hasOwnProperty.call(value, key)) validateSchema(value[key], child, `${pathName}.${key}`);
    }
  }
  if (schema.type === 'array' && Array.isArray(value)) {
    if (schema.maxItems !== undefined && value.length > schema.maxItems) fail(`array too long at ${pathName}`);
    if (schema.minItems !== undefined && value.length < schema.minItems) fail(`array too short at ${pathName}`);
    if (schema.items) value.forEach((item, index) => validateSchema(item, schema.items, `${pathName}[${index}]`));
  }
}

function schemaFor(defName) {
  return spec.$defs[defName];
}

const cases = [
  ['CapabilitiesResponse', surface.capabilities()],
  ['ReceiptViewerResponse', surface.receiptViewer('sha256-missing', {})],
  ['ManifestLockResponse', surface.manifestLock()],
  ['HashChallengeResponse', surface.hashChallenge({ provided_hash: surface.LOCK_SHA256 })],
  ['HashChallengeResponse', surface.hashChallenge({ provided_hash: '0'.repeat(64) })],
  ['WitnessSurfaceResponse', surface.witnessSurface('sha256-test')],
  ['ReplayVerifyResponse', surface.replayVerify({ action: 'verify_manifest_lock' })]
];

const results = [];
let ok = true;

for (const [defName, response] of cases) {
  try {
    surface.assertZeroMutation(response);
    validateSchema(response, schemaFor(defName), defName);
    results.push({ defName, endpoint: response.endpoint, ok: true });
  } catch (error) {
    ok = false;
    results.push({ defName, endpoint: response && response.endpoint, ok: false, error: error.message, details: error.details || null });
  }
}

const report = {
  issue: 'EXT-101',
  title: 'OpenAPI Contract Lock Verification',
  ok,
  checked_cases: results.length,
  results,
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
