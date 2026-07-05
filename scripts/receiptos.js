#!/usr/bin/env node
/*
 * ReceiptOS verifier CLI.
 *
 * Usage:
 *   node scripts/receiptos.js verify <uid> --json
 *   node scripts/receiptos.js verify <uid> --json --tx-hash <base-tx-hash>
 *
 * Exit codes:
 *   0 = PASS
 *   1 = FAIL
 *   2 = PENDING / unavailable / malformed input
 */

const { createPublicClient, http, parseAbi, parseAbiParameters, decodeAbiParameters } = require('viem');
const { base } = require('viem/chains');

const EAS_CONTRACT_BASE = '0x4200000000000000000000000000000000000021';
const RECEIPTOS_SCHEMA_UID = '0x5a535b9ba95c0a8fd86eac8a6db8b75d79213b388a4c25f17b066cc6543d0aa3';
const RECEIPTOS_SCHEMA_NAME = 'RECEIPTOS-ANCHOR-001';
const ZERO_BYTES32 = '0x0000000000000000000000000000000000000000000000000000000000000000';

const EXPECTED = {
  protocol: 'RECEIPTOS-ANCHOR-001',
  project: 'receiptos-base',
  repository: 'jsonwisdom/receiptos-base',
  merge_commit: '95d06d09b0b1ab6896d147ea35d8d235eec7747f',
  receipt_core_hash: '0x776021ffc8f70ff10f31911a7aaa9eb9ae9fc805d21e29eca591a6e36879be5c',
  artifact_sha256: '0x2757b42eff5ffe183315cff32bcf5e2e7420c96c192e463421e59a441b852032',
  demo: 'verify-60-second',
  authority: false,
  version: '1.0.0',
  parent_receipt: ZERO_BYTES32,
  recipient: '0xa380552a27b0a5a2874ea7aa52cac09f542002e8'
};

const easAbi = parseAbi([
  'function getAttestation(bytes32 uid) view returns ((bytes32 uid, bytes32 schema, uint64 time, uint64 expirationTime, uint64 revocationTime, bytes32 refUID, address recipient, address attester, bool revocable, bytes data) attestation)'
]);

const receiptosSchema = parseAbiParameters(
  'string protocol, string project, string repository, string merge_commit, bytes32 receipt_core_hash, bytes32 artifact_sha256, string demo, bool authority, string version, bytes32 parent_receipt'
);

function usage() {
  console.error('Usage: receiptos verify <uid> --json [--rpc-url <url>] [--tx-hash <hash>]');
}

function normalizeHex(value) {
  return typeof value === 'string' ? value.toLowerCase() : value;
}

function isBytes32(value) {
  return /^0x[0-9a-fA-F]{64}$/.test(value || '');
}

function parseArgs(argv) {
  const args = [...argv];
  const command = args.shift();
  const uid = args.shift();
  const parsed = {
    command,
    uid,
    json: false,
    rpcUrl: process.env.BASE_RPC_URL || 'https://mainnet.base.org',
    txHash: null
  };

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--json') parsed.json = true;
    else if (arg === '--rpc-url') parsed.rpcUrl = args[++i];
    else if (arg === '--tx-hash') parsed.txHash = args[++i];
    else if (arg === '--help' || arg === '-h') parsed.help = true;
    else parsed.unknown = arg;
  }

  return parsed;
}

function attestationField(attestation, index, name) {
  return attestation?.[name] ?? attestation?.[index];
}

function buildOutput({ uid, txHash, attestation, decoded, checks, status }) {
  return {
    status,
    authority: false,
    uid: normalizeHex(uid),
    tx_hash: txHash ? normalizeHex(txHash) : null,
    schema: RECEIPTOS_SCHEMA_NAME,
    schema_uid: normalizeHex(attestationField(attestation, 1, 'schema')),
    repository: decoded.repository,
    merge_commit: decoded.merge_commit,
    receipt_core_hash: normalizeHex(decoded.receipt_core_hash),
    artifact_sha256: normalizeHex(decoded.artifact_sha256),
    decoded_payload: decoded,
    checks
  };
}

function emitPending(uid, reason, txHash = null) {
  const output = {
    status: 'PENDING',
    authority: false,
    uid: uid || null,
    tx_hash: txHash || null,
    schema: RECEIPTOS_SCHEMA_NAME,
    checks: {
      uid_resolved: false
    },
    error: reason
  };
  console.log(JSON.stringify(output, null, 2));
  process.exit(2);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help || options.command !== 'verify' || !options.uid || options.unknown) {
    usage();
    process.exit(2);
  }

  if (!isBytes32(options.uid)) {
    emitPending(options.uid, 'UID must be a 32-byte hex string.', options.txHash);
  }

  const client = createPublicClient({
    chain: base,
    transport: http(options.rpcUrl)
  });

  let attestation;
  try {
    attestation = await client.readContract({
      address: EAS_CONTRACT_BASE,
      abi: easAbi,
      functionName: 'getAttestation',
      args: [options.uid]
    });
  } catch (error) {
    emitPending(options.uid, `Unable to fetch attestation: ${error.message || String(error)}`, options.txHash);
  }

  const resolvedUid = normalizeHex(attestationField(attestation, 0, 'uid'));
  if (!resolvedUid || resolvedUid === ZERO_BYTES32) {
    emitPending(options.uid, 'Attestation not found.', options.txHash);
  }

  const data = attestationField(attestation, 9, 'data');
  let values;
  try {
    values = decodeAbiParameters(receiptosSchema, data);
  } catch (error) {
    const checks = {
      uid_resolved: true,
      schema_match: normalizeHex(attestationField(attestation, 1, 'schema')) === RECEIPTOS_SCHEMA_UID,
      decoded_payload: false
    };
    const output = {
      status: 'FAIL',
      authority: false,
      uid: normalizeHex(options.uid),
      tx_hash: options.txHash ? normalizeHex(options.txHash) : null,
      schema: RECEIPTOS_SCHEMA_NAME,
      schema_uid: normalizeHex(attestationField(attestation, 1, 'schema')),
      checks,
      error: `Unable to decode ReceiptOS payload: ${error.message || String(error)}`
    };
    console.log(JSON.stringify(output, null, 2));
    process.exit(1);
  }

  const decoded = {
    protocol: values[0],
    project: values[1],
    repository: values[2],
    merge_commit: values[3],
    receipt_core_hash: normalizeHex(values[4]),
    artifact_sha256: normalizeHex(values[5]),
    demo: values[6],
    authority: values[7],
    version: values[8],
    parent_receipt: normalizeHex(values[9])
  };

  const checks = {
    uid_resolved: resolvedUid === normalizeHex(options.uid),
    schema_match: normalizeHex(attestationField(attestation, 1, 'schema')) === RECEIPTOS_SCHEMA_UID,
    recipient_match: normalizeHex(attestationField(attestation, 6, 'recipient')) === EXPECTED.recipient,
    protocol_match: decoded.protocol === EXPECTED.protocol,
    project_match: decoded.project === EXPECTED.project,
    repository_match: decoded.repository === EXPECTED.repository,
    commit_match: decoded.merge_commit === EXPECTED.merge_commit,
    receipt_hash_match: decoded.receipt_core_hash === EXPECTED.receipt_core_hash,
    artifact_hash_match: decoded.artifact_sha256 === EXPECTED.artifact_sha256,
    demo_match: decoded.demo === EXPECTED.demo,
    authority_false: decoded.authority === false,
    version_match: decoded.version === EXPECTED.version,
    parent_receipt_zero: decoded.parent_receipt === EXPECTED.parent_receipt
  };

  const isPass = Object.values(checks).every(Boolean);
  const output = buildOutput({
    uid: options.uid,
    txHash: options.txHash,
    attestation,
    decoded,
    checks,
    status: isPass ? 'PASS' : 'FAIL'
  });

  console.log(JSON.stringify(output, null, 2));
  process.exit(isPass ? 0 : 1);
}

main().catch((error) => {
  emitPending(null, error.message || String(error));
});
