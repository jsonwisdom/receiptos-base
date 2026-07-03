"use strict";

const { sha256Ref } = require("./canonical");

function policyHashMaterial(policy) {
  return {
    version: policy.policy_version,
    rules: policy.rules || [],
  };
}

function computePolicyHash(policy) {
  return sha256Ref(policyHashMaterial(policy));
}

function toolNotInDenylist(receiptDraft, rule) {
  const denied = new Set(rule.deny_tools || []);
  const toolName = receiptDraft.inputs && receiptDraft.inputs.tool_name;
  return !denied.has(toolName);
}

function requiresCapturedContext(receiptDraft, rule) {
  const actionTypes = new Set(rule.action_types || []);
  if (!actionTypes.has(receiptDraft.action_type)) {
    return true;
  }
  return Array.isArray(receiptDraft.captured_context) && receiptDraft.captured_context.length > 0;
}

const MATCHERS = {
  tool_not_in_denylist: toolNotInDenylist,
  requires_captured_context: requiresCapturedContext,
};

function evaluatePolicy(policy, receiptDraft) {
  const results = (policy.rules || []).map((rule) => {
    const matcher = MATCHERS[rule.matcher];

    // Do not eval policy-authored condition strings here. A generic policy DSL
    // needs a real parser or sandbox before policy files can define expressions.
    if (!matcher) {
      return {
        rule_id: rule.rule_id,
        result: "fail",
        reason: `unknown matcher: ${rule.matcher}`,
      };
    }

    const passed = matcher(receiptDraft, rule);
    return {
      rule_id: rule.rule_id,
      result: passed ? "pass" : "fail",
      reason: passed ? null : rule.description,
    };
  });

  return {
    pass: results.every((result) => result.result === "pass"),
    details: {
      rules: results,
    },
  };
}

module.exports = {
  computePolicyHash,
  evaluatePolicy,
  policyHashMaterial,
};
