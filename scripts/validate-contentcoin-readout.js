'use strict';

const fs = require('node:fs');

const fixturePath = process.argv[2] || 'receipt-schema/contentcoin/v1.1/fixtures/META.candidate.json';
const errors = [];

function fail(message) {
  errors.push(message);
}

function isAddress(value) {
  return typeof value === 'string' && /^0x[0-9a-fA-F]{40}$/.test(value);
}

function isKeccak256(value) {
  return typeof value === 'string' && /^0x[0-9a-fA-F]{64}$/.test(value);
}

function isHolderPlaceholder(value) {
  return typeof value === 'string' && /^HOLDER_[1-9][0-9]*$/.test(value);
}

let seal;
try {
  seal = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
} catch (error) {
  console.error(`READOUT_SEAL validation failed: cannot parse ${fixturePath}: ${error.message}`);
  process.exit(1);
}

if (seal.seal_version !== 'READOUT_SEAL_V1_1') fail('seal_version must be READOUT_SEAL_V1_1');
if (seal.network !== 'base') fail('network must be base');
if (!isAddress(seal.contract_address)) fail('contract_address must be an EVM address');
if (seal.token_standard !== 'ERC20_PROXY') fail('token_standard must be ERC20_PROXY');
if (seal.token_pattern !== 'CONTENTCOIN') fail('token_pattern must be CONTENTCOIN');
if (seal.max_total_supply !== '1000000000') fail('max_total_supply must be 1000000000');
if (seal.authority !== false) fail('authority must be false');

const deployment = seal.deployment || {};
if (deployment.deployed_contract !== seal.contract_address) fail('deployment.deployed_contract must equal contract_address');
if (!(deployment.tx_sender === 'HOLD' || isAddress(deployment.tx_sender))) fail('deployment.tx_sender must be HOLD or an EVM address');
if (!(deployment.factory_address === 'HOLD' || isAddress(deployment.factory_address))) fail('deployment.factory_address must be HOLD or an EVM address');
if (!(deployment.deploy_block === 'HOLD' || (Number.isInteger(deployment.deploy_block) && deployment.deploy_block >= 0))) fail('deployment.deploy_block must be HOLD or a non-negative integer');
if (!(deployment.deployed_at === 'HOLD' || (typeof deployment.deployed_at === 'string' && !Number.isNaN(Date.parse(deployment.deployed_at))))) fail('deployment.deployed_at must be HOLD or an ISO-like timestamp');

const liquidity = seal.liquidity || {};
if (!['UNKNOWN', 'NO_POOL', 'POOL_FOUND'].includes(liquidity.pool_status)) fail('liquidity.pool_status must be UNKNOWN, NO_POOL, or POOL_FOUND');
if (liquidity.pool_status === 'UNKNOWN' && liquidity.pool_address !== 'HOLD') fail('UNKNOWN liquidity requires pool_address = HOLD');
if (liquidity.pool_status === 'NO_POOL' && liquidity.pool_address !== null) fail('NO_POOL requires pool_address = null');
if (liquidity.pool_status === 'POOL_FOUND' && !isAddress(liquidity.pool_address)) fail('POOL_FOUND requires an EVM pool address');

const holders = seal.holders || {};
if (!(holders.snapshot_block === 'HOLD' || (Number.isInteger(holders.snapshot_block) && holders.snapshot_block >= 0))) fail('holders.snapshot_block must be HOLD or a non-negative integer');
if (!Number.isInteger(holders.count_at_snapshot) || holders.count_at_snapshot < 0) fail('holders.count_at_snapshot must be a non-negative integer');
if (!Array.isArray(holders.addresses)) {
  fail('holders.addresses must be an array');
} else {
  if (holders.count_at_snapshot !== holders.addresses.length) fail('holders.count_at_snapshot must equal holders.addresses.length');
  for (const holder of holders.addresses) {
    if (!(isAddress(holder) || isHolderPlaceholder(holder))) fail(`invalid holder reference: ${holder}`);
  }
}

const economics = seal.economics || {};
if (economics.creator_coin_economics !== false) fail('creator_coin_economics must remain false');
if (!['HOLD', 'POST_2025_09_15_1PCT'].includes(economics.fee_model)) fail('fee_model is outside the READOUT_SEAL_V1_1 allowlist');

const implementation = seal.implementation || {};
if (!(implementation.implementation_contract === 'HOLD' || isAddress(implementation.implementation_contract))) fail('implementation_contract must be HOLD or an EVM address');
if (!(implementation.runtime_bytecode_keccak256 === 'HOLD' || isKeccak256(implementation.runtime_bytecode_keccak256))) fail('runtime_bytecode_keccak256 must be HOLD or a 32-byte hash');

const metadata = seal.metadata || {};
if (!(metadata.metadata_uri === 'HOLD' || (typeof metadata.metadata_uri === 'string' && /^(ipfs|https?|ar):/.test(metadata.metadata_uri)))) fail('metadata_uri must be HOLD or a supported URI');
if (!(metadata.metadata_json_keccak256 === 'HOLD' || isKeccak256(metadata.metadata_json_keccak256))) fail('metadata_json_keccak256 must be HOLD or a 32-byte hash');

const provenance = seal.provenance_chain || {};
for (const key of ['factory', 'implementation', 'creator_wallet']) {
  if (!(provenance[key] === 'HOLD' || isAddress(provenance[key]))) fail(`provenance_chain.${key} must be HOLD or an EVM address`);
}
if (!(provenance.metadata_uri === 'HOLD' || (typeof provenance.metadata_uri === 'string' && /^(ipfs|https?|ar):/.test(provenance.metadata_uri)))) fail('provenance_chain.metadata_uri must be HOLD or a supported URI');
if (typeof provenance.post_id !== 'string' || provenance.post_id.length === 0) fail('provenance_chain.post_id must be a non-empty string');
if (!(provenance.initial_pool === 'HOLD' || provenance.initial_pool === null || isAddress(provenance.initial_pool))) fail('provenance_chain.initial_pool must be HOLD, null, or an EVM address');
if (!Array.isArray(provenance.holders_at_snapshot)) {
  fail('provenance_chain.holders_at_snapshot must be an array');
} else if (Array.isArray(holders.addresses) && JSON.stringify(provenance.holders_at_snapshot) !== JSON.stringify(holders.addresses)) {
  fail('provenance_chain.holders_at_snapshot must match holders.addresses');
}
if (!Array.isArray(provenance.trades)) fail('provenance_chain.trades must be an array');
if (!Array.isArray(provenance.rewards)) fail('provenance_chain.rewards must be an array');

const gates = seal.constitutional_gates || {};
if (!['HOLD', 'TRUE', 'FALSE'].includes(gates.caller_anchor_match)) fail('caller_anchor_match must be HOLD, TRUE, or FALSE');
if (!['HOLD', 'TRUE', 'FALSE'].includes(gates.payout_recipient_anchor_match)) fail('payout_recipient_anchor_match must be HOLD, TRUE, or FALSE');
if (gates.platform_referrer_role !== 'ECONOMIC_ATTRIBUTION_ONLY') fail('platform_referrer_role must be ECONOMIC_ATTRIBUTION_ONLY');

const status = seal.status || {};
if (status.event_status !== 'IMMUTABLE') fail('event_status must be IMMUTABLE');
if (status.snapshot_status !== 'POINT_IN_TIME') fail('snapshot_status must be POINT_IN_TIME');
if (status.interpretation_status !== 'ACTIVE') fail('interpretation_status must be ACTIVE');
if (status.correction_status !== 'APPEND_ONLY') fail('correction_status must be APPEND_ONLY');
if (!['HOLD', 'LOW', 'MEDIUM', 'HIGH'].includes(status.provenance_confidence)) fail('invalid provenance_confidence');

const unresolved = [
  deployment.tx_sender,
  deployment.factory_address,
  deployment.deploy_block,
  deployment.deployed_at,
  liquidity.pool_status === 'UNKNOWN' ? 'HOLD' : liquidity.pool_address,
  holders.snapshot_block,
  economics.fee_model,
  implementation.implementation_contract,
  implementation.runtime_bytecode_keccak256,
  metadata.metadata_uri,
  metadata.metadata_json_keccak256,
  provenance.factory,
  provenance.implementation,
  provenance.creator_wallet,
  provenance.metadata_uri,
  provenance.post_id,
  provenance.initial_pool,
  gates.caller_anchor_match,
  gates.payout_recipient_anchor_match
].some((value) => value === 'HOLD');

const holderPlaceholders = (Array.isArray(holders.addresses) && holders.addresses.some(isHolderPlaceholder)) ||
  (Array.isArray(provenance.holders_at_snapshot) && provenance.holders_at_snapshot.some(isHolderPlaceholder));

if ((unresolved || holderPlaceholders) && status.provenance_confidence !== 'HOLD') {
  fail('unresolved fields or holder placeholders require provenance_confidence = HOLD');
}

if (errors.length > 0) {
  console.error('READOUT_SEAL validation failed:');
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(JSON.stringify({
  validator: 'READOUT_SEAL_V1_1_CONTENTCOIN_GATE',
  fixture: fixturePath,
  status: 'PASS',
  authority: false,
  provenance_confidence: status.provenance_confidence,
  canonical: false
}, null, 2));
