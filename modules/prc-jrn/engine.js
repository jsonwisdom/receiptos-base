#!/usr/bin/env node
'use strict';

const crypto = require('crypto');

const CONSTITUTION = Object.freeze([
  'Observation != Assessment',
  'Questions before conclusions.',
  'Verification before confidence.',
  'Evidence updates assessments.',
  'Revision is a strength.',
  'Unknowns define the perimeter of the audit.'
]);

const ENGINE_SEQUENCE = Object.freeze([
  'Question',
  'Source',
  'Evidence',
  'Replay / Reproducibility',
  'Assessment',
  'Revision'
]);

const CONSTITUTION_SHA256 = '63bef9d6e3906d34a44a6ea2b1212cb13cc26aed94cadff7acd880b3f664afb2';
const ENGINE_SHA256 = '90fe8c4d010acbc8883af840920014595799d24efb25d8fa191b8e261e043c8d';

const CASES = Object.freeze({
  '001': {
    title: 'The Viral Investment',
    distinction: 'Attention != Evidence',
    claim_template: 'This new token will 100x by next month.',
    prompts: [
      'What is the original source of the prediction?',
      'What evidence supports the projection?',
      'Is there independent analysis?',
      'What historical comparisons are relevant?',
      'What would falsify the claim?'
    ]
  },
  '002': {
    title: 'The Scientific Breakthrough',
    distinction: 'Headline != Research',
    claim_template: 'A new study changes everything.',
    prompts: [
      'Where is the original paper?',
      'Has it been peer reviewed?',
      'Are methods and data available?',
      'Has the result been independently replicated?',
      'What limitations did the authors state?'
    ]
  },
  '003': {
    title: 'The Breaking News Story',
    distinction: 'Speed != Verification',
    claim_template: 'Something huge is happening right now.',
    prompts: [
      'What is the original source?',
      'What is confirmed?',
      'What is still unknown?',
      'Is there independent corroboration?',
      'What evidence would update the assessment?'
    ]
  },
  '004': {
    title: 'The High-Fidelity Illusion',
    distinction: 'Media Quality != Evidence Quality',
    claim_template: 'The video shows exactly what happened.',
    prompts: [
      'Can the file be traced to the raw capture source?',
      'Is metadata available or stripped?',
      'Is chain of custody documented?',
      'Does the context match public records?',
      'Has independent verification occurred?'
    ]
  },
  '005': {
    title: 'Context Collapse',
    distinction: 'Accurate Fact != Complete Context',
    claim_template: 'The quote is real, so the claim is true.',
    prompts: [
      'Is the original source located?',
      'Is the full surrounding context available?',
      'What material omissions may exist?',
      'Does interpretation go beyond the evidence?',
      'What additional context would change the assessment?'
    ]
  },
  '006': {
    title: 'Causation Mirage',
    distinction: 'Correlation != Causation',
    claim_template: 'After Policy X was introduced, Event Y increased. Therefore, Policy X caused Event Y.',
    prompts: [
      'Is the original dataset available?',
      'Is temporal sequence verified?',
      'Are alternative explanations considered?',
      'Is there a comparison group?',
      'Is there causal evidence or only circumstantial evidence?'
    ]
  }
});

function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map(canonicalize);
  }
  if (value && typeof value === 'object') {
    return Object.keys(value).sort().reduce((acc, key) => {
      acc[key] = canonicalize(value[key]);
      return acc;
    }, {});
  }
  return value;
}

function canonicalJSONString(value) {
  return JSON.stringify(canonicalize(value));
}

function sha256(value) {
  return crypto.createHash('sha256').update(value, 'utf8').digest('hex');
}

function assertAnchorIntegrity() {
  const constitutionHash = sha256(canonicalJSONString(CONSTITUTION));
  const engineHash = sha256(canonicalJSONString(ENGINE_SEQUENCE));
  if (constitutionHash !== CONSTITUTION_SHA256) {
    throw new Error(`constitution drift: expected ${CONSTITUTION_SHA256}, got ${constitutionHash}`);
  }
  if (engineHash !== ENGINE_SHA256) {
    throw new Error(`engine drift: expected ${ENGINE_SHA256}, got ${engineHash}`);
  }
  return { constitution_sha256: constitutionHash, engine_sha256: engineHash };
}

function createFieldReceipt(input) {
  assertAnchorIntegrity();

  const caseDef = CASES[input.case_id];
  if (!caseDef) {
    throw new Error(`unknown case_id: ${input.case_id}`);
  }

  const receipt = {
    receipt_id: input.receipt_id,
    framework_version: 'PRC-JRN-v1.1',
    case_id: input.case_id,
    mode: input.mode || 'simulated_validation',
    session: input.session || {},
    claim_reviewed: input.claim_reviewed || caseDef.claim_template,
    baseline_assessment: input.baseline_assessment || 'under_review',
    final_assessment: input.final_assessment || 'under_review',
    observations: input.observations || [],
    unknowns: input.unknowns || [],
    evidence_introduced: input.evidence_introduced || [],
    observed_behaviors: input.observed_behaviors || {
      asked_for_primary_source: false,
      distinguished_observation_from_assessment: false,
      identified_unknowns: false,
      requested_corroboration: false,
      revised_assessment: false,
      explained_revision: false
    },
    friction: input.friction || [],
    curriculum_delta: input.curriculum_delta || [],
    constitution_changes_proposed: [],
    engine_changes_proposed: [],
    hashes: {
      constitution_sha256: CONSTITUTION_SHA256,
      engine_sha256: ENGINE_SHA256
    },
    authority: false
  };

  receipt.hashes.receipt_sha256 = sha256(canonicalJSONString({
    ...receipt,
    hashes: {
      constitution_sha256: CONSTITUTION_SHA256,
      engine_sha256: ENGINE_SHA256
    }
  }));

  return receipt;
}

function indexExternalReceipt(index, receipt) {
  assertAnchorIntegrity();
  if (!receipt.receipt_id || !receipt.receipt_id.startsWith('PRC-JRN-FIELD-EXT-')) {
    throw new Error('external receipts must use PRC-JRN-FIELD-EXT-* receipt_id');
  }
  if (receipt.mode !== 'external_validation' && receipt.mode !== 'classroom' && receipt.mode !== 'workshop' && receipt.mode !== 'pilot') {
    throw new Error('external receipt mode must be external_validation, classroom, workshop, or pilot');
  }
  if (receipt.authority !== false) {
    throw new Error('receipt authority must be false');
  }
  return {
    ...index,
    receipts_indexed: [...(index.receipts_indexed || []), receipt.receipt_id],
    external_receipts_pending: Math.max(0, (index.external_receipts_pending || 0) - 1),
    last_indexed_receipt: receipt.receipt_id
  };
}

if (require.main === module) {
  const anchors = assertAnchorIntegrity();
  const sample = createFieldReceipt({
    receipt_id: 'PRC-JRN-FIELD-001',
    case_id: '003',
    claim_reviewed: 'Something huge is happening right now.',
    final_assessment: 'insufficient_evidence',
    observed_behaviors: {
      asked_for_primary_source: true,
      distinguished_observation_from_assessment: true,
      identified_unknowns: true,
      requested_corroboration: true,
      revised_assessment: true,
      explained_revision: true
    },
    curriculum_delta: ['Add urgency-as-trigger module to Case 003.']
  });
  console.log(JSON.stringify({ ok: true, anchors, sample_receipt_hash: sample.hashes.receipt_sha256 }, null, 2));
}

module.exports = {
  CONSTITUTION,
  ENGINE_SEQUENCE,
  CONSTITUTION_SHA256,
  ENGINE_SHA256,
  CASES,
  canonicalize,
  canonicalJSONString,
  sha256,
  assertAnchorIntegrity,
  createFieldReceipt,
  indexExternalReceipt
};
