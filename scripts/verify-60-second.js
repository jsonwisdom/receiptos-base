#!/usr/bin/env node
const fs = require('fs');
const crypto = require('crypto');

const path = process.argv[2] || 'examples/verify-60-second/receipt.sample.json';
const receipt = JSON.parse(fs.readFileSync(path, 'utf8'));

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function canonical(value) {
  if (Array.isArray(value)) {
    return '[' + value.map(canonical).join(',') + ']';
  }
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map((key) => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
  }
  return JSON.stringify(value);
}

const declaredReceiptHash = receipt.receipt_core_hash;
const core = { ...receipt };
delete core.receipt_core_hash;

const artifactHash = sha256(receipt.artifact_text);
const receiptHash = sha256(canonical(core));

const checks = [
  ['artifact_sha256', artifactHash === receipt.artifact_sha256],
  ['receipt_core_hash', receiptHash === declaredReceiptHash],
  ['authority_false', receipt.authority === false],
  ['witness_only_true', receipt.witness_only === true],
  ['truth_claim_false', receipt.truth_claim === false],
  ['anchor_commit_present', Boolean(receipt.anchor && receipt.anchor.commit)]
];

for (const [name, pass] of checks) {
  console.log(`${name}=${pass ? 'PASS' : 'FAIL'}`);
}

console.log(`computed_artifact_sha256=${artifactHash}`);
console.log(`computed_receipt_core_hash=${receiptHash}`);

if (checks.some(([, pass]) => !pass)) {
  console.error('RECEIPTOS_60_SECOND_VERIFY=FAIL');
  process.exit(1);
}

console.log('RECEIPTOS_60_SECOND_VERIFY=PASS');
