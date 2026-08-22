'use strict';

const fs = require('node:fs');
const crypto = require('node:crypto');

const ALLOW = {
  DEPLOY_TX_RECEIPT_V1: ['deployment.tx_sender','deployment.factory_address','deployment.deployed_at'],
  FACTORY_TRACE_RECEIPT_V1: ['provenance_chain.factory'],
  IMPLEMENTATION_RECEIPT_V1: ['implementation.implementation_contract','implementation.runtime_bytecode_keccak256','provenance_chain.implementation'],
  METADATA_RECEIPT_V1: ['metadata.metadata_uri','metadata.metadata_json_keccak256','provenance_chain.metadata_uri','provenance_chain.post_id'],
  POOL_RECEIPT_V1: ['liquidity.pool_status','liquidity.pool_address','provenance_chain.initial_pool'],
  HOLDER_SNAPSHOT_RECEIPT_V1: ['holders.snapshot_block','holders.addresses','provenance_chain.holders_at_snapshot'],
  ANCHOR_MATCH_RECEIPT_V1: ['constitutional_gates.caller_anchor_match','constitutional_gates.payout_recipient_anchor_match','provenance_chain.creator_wallet'],
  PROVENANCE_CONFIDENCE_RECEIPT_V1: ['status.provenance_confidence']
};

const ADDRESS = /^0x[0-9a-fA-F]{40}$/;
const HASH32 = /^0x[0-9a-fA-F]{64}$/;
const HOLDER = /^HOLDER_[1-9][0-9]*$/;

function reject(message) { throw new Error(message); }
function clone(v) { return JSON.parse(JSON.stringify(v)); }
function get(root, path) { return path.split('.').reduce((v,k) => v == null ? undefined : v[k], root); }
function set(root, path, value) {
  const keys = path.split('.'); const leaf = keys.pop(); let cur = root;
  for (const key of keys) { if (!cur[key] || typeof cur[key] !== 'object') reject(`missing object for ${path}`); cur = cur[key]; }
  cur[leaf] = value;
}
function stable(v) {
  if (Array.isArray(v)) return v.map(stable);
  if (v && typeof v === 'object') return Object.keys(v).sort().reduce((o,k) => (o[k]=stable(v[k]),o),{});
  return v;
}
function sha256(v) { return crypto.createHash('sha256').update(v).digest('hex'); }
function unresolved(v) { return v === 'HOLD' || v === 'UNKNOWN' || (Array.isArray(v) && v.some(x => typeof x === 'string' && HOLDER.test(x))); }

function assertCandidate(c) {
  if (c.seal_version !== 'READOUT_SEAL_V1_1') reject('seal_version mismatch');
  if (c.network !== 'base') reject('network must be base');
  if (!ADDRESS.test(c.contract_address || '')) reject('contract_address invalid');
  if (c.authority !== false) reject('authority must remain false');
  if (c.status?.event_status !== 'IMMUTABLE') reject('event_status must be IMMUTABLE');
  if (c.status?.correction_status !== 'APPEND_ONLY') reject('correction_status must be APPEND_ONLY');
}

function assertBatch(b, c) {
  if (b.resolver_version !== 'PROVENANCE_CHAIN_RESOLVER_V0_1') reject('resolver_version mismatch');
  if (b.network !== c.network || (b.contract_address || '').toLowerCase() !== c.contract_address.toLowerCase()) reject('batch target mismatch');
  if (b.seal_version !== c.seal_version) reject('batch seal mismatch');
  if (b.authority !== false) reject('batch authority must be false');
  if (!b.resolution_id) reject('resolution_id required');
  if (!b.observed_at || Number.isNaN(Date.parse(b.observed_at))) reject('observed_at invalid');
  if (!Array.isArray(b.receipts)) reject('receipts must be an array');
}

function assertValue(path, value) {
  if (['deployment.tx_sender','deployment.factory_address','provenance_chain.factory','provenance_chain.implementation','provenance_chain.creator_wallet','implementation.implementation_contract'].includes(path) && !ADDRESS.test(value || '')) reject(`${path} must be an EVM address`);
  if (['implementation.runtime_bytecode_keccak256','metadata.metadata_json_keccak256'].includes(path) && !HASH32.test(value || '')) reject(`${path} must be a 32-byte 0x hash`);
  if (path === 'holders.snapshot_block' && (!Number.isInteger(value) || value < 0)) reject('holders.snapshot_block invalid');
  if (['holders.addresses','provenance_chain.holders_at_snapshot'].includes(path) && (!Array.isArray(value) || !value.every(v => ADDRESS.test(v)))) reject(`${path} must be EVM addresses`);
  if (['constitutional_gates.caller_anchor_match','constitutional_gates.payout_recipient_anchor_match'].includes(path) && ![true,false,'TRUE','FALSE'].includes(value)) reject(`${path} must be boolean or legacy TRUE/FALSE`);
  if (path === 'status.provenance_confidence' && !['LOW','MEDIUM','HIGH'].includes(value)) reject('provenance_confidence invalid');
  if (path === 'liquidity.pool_status' && !['NO_POOL','POOL_FOUND'].includes(value)) reject('pool_status must resolve to NO_POOL or POOL_FOUND');
  if (value === 'HOLD' || value === 'UNKNOWN') reject(`${path} cannot resolve to unresolved sentinel`);
}

function assertTransition(path, before, after) {
  if (path === 'liquidity.pool_status') { if (before !== 'UNKNOWN') reject('pool_status already resolved'); return; }
  if (['holders.addresses','provenance_chain.holders_at_snapshot'].includes(path)) { if (!Array.isArray(before) || !before.some(v => typeof v === 'string' && HOLDER.test(v))) reject(`${path} already resolved`); return; }
  if (!unresolved(before)) reject(`${path} already resolved; overwrite forbidden`);
  assertValue(path, after);
}

function unresolvedPaths(s) {
  const paths = [
    'deployment.tx_sender','deployment.factory_address','deployment.deployed_at',
    'liquidity.pool_status','liquidity.pool_address','holders.snapshot_block','holders.addresses',
    'implementation.implementation_contract','implementation.runtime_bytecode_keccak256',
    'metadata.metadata_uri','metadata.metadata_json_keccak256','provenance_chain.factory',
    'provenance_chain.implementation','provenance_chain.creator_wallet','provenance_chain.metadata_uri',
    'provenance_chain.post_id','provenance_chain.initial_pool','provenance_chain.holders_at_snapshot',
    'constitutional_gates.caller_anchor_match','constitutional_gates.payout_recipient_anchor_match'
  ];
  return paths.filter(path => {
    const value = get(s,path);
    if ((path === 'liquidity.pool_address' || path === 'provenance_chain.initial_pool') && s.liquidity?.pool_status === 'NO_POOL' && value === null) return false;
    return unresolved(value);
  });
}

function consistency(s) {
  const lower = v => typeof v === 'string' ? v.toLowerCase() : v;
  if (s.deployment.factory_address !== 'HOLD' && s.provenance_chain.factory !== 'HOLD' && lower(s.deployment.factory_address) !== lower(s.provenance_chain.factory)) reject('factory mismatch');
  if (s.implementation.implementation_contract !== 'HOLD' && s.provenance_chain.implementation !== 'HOLD' && lower(s.implementation.implementation_contract) !== lower(s.provenance_chain.implementation)) reject('implementation mismatch');
  if (s.metadata.metadata_uri !== 'HOLD' && s.provenance_chain.metadata_uri !== 'HOLD' && s.metadata.metadata_uri !== s.provenance_chain.metadata_uri) reject('metadata URI mismatch');
  if (s.liquidity.pool_status === 'NO_POOL' && (s.liquidity.pool_address !== null || s.provenance_chain.initial_pool !== null)) reject('NO_POOL requires null pool fields');
  if (s.liquidity.pool_status === 'POOL_FOUND' && (!ADDRESS.test(s.liquidity.pool_address || '') || !ADDRESS.test(s.provenance_chain.initial_pool || ''))) reject('POOL_FOUND requires pool addresses');
  if (s.holders.count_at_snapshot !== s.holders.addresses.length) reject('holder count mismatch');
  if (JSON.stringify(s.holders.addresses) !== JSON.stringify(s.provenance_chain.holders_at_snapshot)) reject('holder snapshot mismatch');
  if (s.authority !== false) reject('authority must remain false');
}

function resolve(candidateBytes, batch) {
  const candidate = JSON.parse(candidateBytes.toString('utf8'));
  assertCandidate(candidate); assertBatch(batch,candidate);
  const next = clone(candidate); const receiptIds = [];

  for (const r of batch.receipts) {
    if (!ALLOW[r.receipt_type]) reject(`unsupported receipt_type ${r.receipt_type}`);
    if (r.authority !== false || r.network !== candidate.network || (r.contract_address || '').toLowerCase() !== candidate.contract_address.toLowerCase()) reject(`${r.receipt_type} target/authority mismatch`);
    if (!r.observed_at || Number.isNaN(Date.parse(r.observed_at)) || !r.source) reject(`${r.receipt_type} missing source/timestamp`);
    if (!Array.isArray(r.releases) || r.releases.length === 0) reject(`${r.receipt_type} releases required`);
    for (const release of r.releases) {
      if (!ALLOW[r.receipt_type].includes(release.path)) reject(`${r.receipt_type} cannot release ${release.path}`);
      assertTransition(release.path, get(next,release.path), release.value);
      assertValue(release.path, release.value);
      set(next,release.path,release.value);
    }
    receiptIds.push({receipt_type:r.receipt_type, receipt_sha256:sha256(JSON.stringify(stable(r)))});
  }

  consistency(next);
  const holds = unresolvedPaths(next);
  if (next.status.provenance_confidence !== 'HOLD' && holds.length) reject(`fake green blocked; unresolved: ${holds.join(', ')}`);

  return {
    resolver_version:'PROVENANCE_CHAIN_RESOLVER_V0_1',
    resolution_id:batch.resolution_id,
    observed_at:batch.observed_at,
    network:candidate.network,
    contract_address:candidate.contract_address,
    seal_version:candidate.seal_version,
    previous_state_sha256:sha256(candidateBytes),
    receipt_ids:receiptIds,
    unresolved_paths:holds,
    next_state:next,
    mutation_model:'APPEND_NEW_STATE_PRESERVE_PRIOR_STATE',
    authority:false
  };
}

function selfTest() {
  const c={seal_version:'READOUT_SEAL_V1_1',network:'base',contract_address:'0x1111111111111111111111111111111111111111',deployment:{tx_sender:'HOLD',factory_address:'HOLD',deployed_contract:'0x1111111111111111111111111111111111111111',deploy_block:1,deployed_at:'HOLD'},liquidity:{pool_status:'UNKNOWN',pool_address:'HOLD'},holders:{snapshot_block:'HOLD',count_at_snapshot:2,addresses:['HOLDER_1','HOLDER_2']},implementation:{implementation_contract:'HOLD',runtime_bytecode_keccak256:'HOLD'},metadata:{metadata_uri:'HOLD',metadata_json_keccak256:'HOLD'},provenance_chain:{factory:'HOLD',implementation:'HOLD',creator_wallet:'HOLD',metadata_uri:'HOLD',post_id:'HOLD',initial_pool:'HOLD',holders_at_snapshot:['HOLDER_1','HOLDER_2']},constitutional_gates:{caller_anchor_match:'HOLD',payout_recipient_anchor_match:'HOLD',platform_referrer_role:'ECONOMIC_ATTRIBUTION_ONLY'},status:{event_status:'IMMUTABLE',snapshot_status:'POINT_IN_TIME',interpretation_status:'ACTIVE',correction_status:'APPEND_ONLY',provenance_confidence:'HOLD'},authority:false};
  const b={resolver_version:'PROVENANCE_CHAIN_RESOLVER_V0_1',resolution_id:'SELFTEST',observed_at:'2026-01-01T00:00:00Z',network:'base',contract_address:c.contract_address,seal_version:c.seal_version,authority:false,receipts:[{receipt_type:'DEPLOY_TX_RECEIPT_V1',observed_at:'2026-01-01T00:00:00Z',network:'base',contract_address:c.contract_address,source:'SELF_TEST_ONLY',authority:false,releases:[{path:'deployment.tx_sender',value:'0x2222222222222222222222222222222222222222'},{path:'deployment.factory_address',value:'0x3333333333333333333333333333333333333333'},{path:'deployment.deployed_at',value:'2026-01-01T00:00:00Z'}]},{receipt_type:'FACTORY_TRACE_RECEIPT_V1',observed_at:'2026-01-01T00:00:00Z',network:'base',contract_address:c.contract_address,source:'SELF_TEST_ONLY',authority:false,releases:[{path:'provenance_chain.factory',value:'0x3333333333333333333333333333333333333333'}]}]};
  const out=resolve(Buffer.from(JSON.stringify(c)),b);
  if (out.next_state.deployment.tx_sender === 'HOLD' || out.next_state.status.provenance_confidence !== 'HOLD') reject('self-test failed');
  console.log(JSON.stringify({resolver:out.resolver_version,status:'PASS',fake_green_blocked:true,authority:false},null,2));
}

if (process.argv.includes('--self-test')) selfTest();
else {
  const [candidatePath,batchPath,outputPath]=process.argv.slice(2);
  if (!candidatePath || !batchPath || !outputPath) { console.error('usage: node scripts/provenance-chain-resolver-v0_1.js <META.candidate.json> <resolution-batch.json> <output.json>'); process.exit(2); }
  try {
    const candidateBytes=fs.readFileSync(candidatePath); const batch=JSON.parse(fs.readFileSync(batchPath,'utf8')); const out=resolve(candidateBytes,batch);
    fs.writeFileSync(outputPath,JSON.stringify(out,null,2)+'\n',{flag:'wx'});
    console.log(JSON.stringify({resolver:out.resolver_version,status:'PASS',receipt_count:out.receipt_ids.length,unresolved_count:out.unresolved_paths.length,output:outputPath,authority:false},null,2));
  } catch (e) { console.error(JSON.stringify({resolver:'PROVENANCE_CHAIN_RESOLVER_V0_1',status:'REJECT',error:e.message,authority:false},null,2)); process.exit(1); }
}
