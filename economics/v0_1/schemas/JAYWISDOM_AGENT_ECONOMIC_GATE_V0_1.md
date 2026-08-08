# JAYWISDOM_AGENT_ECONOMIC_GATE_V0_1

Status: SPECIFICATION  
Authority: FALSE  
No Fake Green: TRUE

## Purpose

Define the deterministic economic eligibility gate for value-moving agent actions.

The objective is:

```text
MAXIMIZE_VERIFIED_NET_PROFIT
```

subject to explicit authority, spend, risk, and human-review bounds.

This specification does not grant execution authority. `ECONOMICALLY_ELIGIBLE` means only that an opportunity passed the economic gate. A later, separate Base MCP execution-authorization receipt is still required before value may move.

## Contract Order

```text
JAYWISDOM_AGENT_ECONOMICS_V0_1
        ↓
ECONOMIC_DECISION_RECEIPT_V0_1
        ↓
existing Base MCP membrane
permission_policy → action_receipt → activation-review → witness → confirmed-payment
        ↓
REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1
```

The economic schemas compose with the existing control plane. They do not bypass it.

## Pre-Execution Recompute Rules

All seven forecast cost components are required. Zero is valid. Omission is invalid.

```text
EXPECTED_TOTAL_COST =
    expected_model_usd
  + expected_data_usd
  + expected_gas_usd
  + expected_bridge_usd
  + expected_slippage_usd
  + expected_failure_reserve_usd
  + expected_other_usd

EXPECTED_NET_PROFIT =
    expected_revenue_usd - EXPECTED_TOTAL_COST

EXPECTED_MARGIN_PCT =
    (EXPECTED_NET_PROFIT / expected_revenue_usd) * 100
    if expected_revenue_usd > 0
    else 0
```

The evaluator MUST recompute these values. A stored value that disagrees with recomputation causes semantic validation to fail.

`expected_slippage_usd` records dollar impact. `expected_slippage_bps` records the rate used by the policy predicate. Both are required.

## Required Policy Limits

Every economics policy MUST provide all nine limits:

```text
max_cost_usd
min_expected_revenue_usd
min_expected_profit_usd
min_margin_pct
max_gas_usd
max_bridge_cost_usd
max_model_cost_usd
max_slippage_bps
max_failure_probability
```

Missing does not mean unlimited. Missing means fail closed.

The decision receipt MUST snapshot these nine values plus `policy_version` and `policy_hash` in `limits_evaluated`.

`policy_hash` is the lowercase 64-hex SHA-256 digest of the exact UTF-8 bytes of the policy instance used for the decision.

## Deterministic Economic Decision

Inputs external to this schema, including authority-envelope validity and spend-policy validity, MUST be resolved from the referenced Base MCP authority surfaces.

```text
HARD_PASS =
    authority_valid
    AND spend_policy_valid
    AND expected_revenue_usd >= min_expected_revenue_usd
    AND expected_net_profit_usd >= min_expected_profit_usd
    AND expected_margin_pct >= min_margin_pct
    AND expected_total_cost_usd <= max_cost_usd
    AND expected_gas_usd <= max_gas_usd
    AND expected_bridge_usd <= max_bridge_cost_usd
    AND expected_model_usd <= max_model_cost_usd
    AND expected_slippage_bps <= max_slippage_bps
    AND failure_probability_estimate <= max_failure_probability
```

Decision:

```text
if forecast is incomplete or any hard predicate fails:
    REJECT

else if human_override_required == true:
    HUMAN_REVIEW

else:
    ECONOMICALLY_ELIGIBLE
```

There is no implicit or subjective `borderline` state in V0.1. Any future borderline-review rule requires an explicit policy field and a versioned schema change.

## Semantic Validation

Schema validity is not arithmetic validity.

```text
schema_valid ≠ semantic_valid
```

Allowed values:

```text
PENDING
PASS
FAIL
```

`PASS` is earned only when the evaluator recomputes the arithmetic, validates the policy snapshot, and confirms that the recorded decision matches the deterministic gate.

A correctly computed `REJECT` receipt may have `semantic_validation = PASS`. PASS means the receipt is internally and semantically consistent; it does not mean the opportunity is approved.

`PENDING` and `FAIL` receipts are not eligible to advance into execution authorization.

Receipts are immutable. Revalidation MUST NOT rewrite a prior receipt; it emits separate verifier/replay evidence.

## Authority Boundary

```text
ECONOMICALLY_ELIGIBLE ≠ EXECUTION_AUTHORIZED
ECONOMIC_DECISION_RECEIPT ≠ EXECUTION_AUTHORIZATION_RECEIPT
SCHEMA_VALID ≠ SEMANTICALLY_VALID
SEMANTICALLY_VALID ≠ PAYMENT_CONFIRMED
TRANSACTION_WITNESS ≠ AGENT_PAY_EXECUTION
```

Every economics artifact carries:

```text
authority = false
no_fake_green = true
```

A model judgment, economic score, forecast, schema, receipt, replay, or attestation creates no execution authority.

## Post-Execution Recompute Rules

All seven realized cost components are required. Zero is valid. Omission is invalid.

```text
REALIZED_TOTAL_COST =
    realized_model_usd
  + realized_data_usd
  + realized_gas_usd
  + realized_bridge_usd
  + realized_slippage_usd
  + realized_failure_loss_usd
  + realized_other_usd

REALIZED_NET_PROFIT =
    realized_revenue_usd - REALIZED_TOTAL_COST

REALIZED_MARGIN_PCT =
    (REALIZED_NET_PROFIT / realized_revenue_usd) * 100
    if realized_revenue_usd > 0
    else 0
```

Forecast variance MUST also be recomputed from the referenced decision receipt:

```text
revenue_variance_usd =
    realized_revenue_usd - expected_revenue_usd

cost_variance_usd =
    realized_total_cost_usd - expected_total_cost_usd

profit_variance_usd =
    realized_net_profit_usd - expected_net_profit_usd

margin_variance_pct =
    realized_margin_pct - expected_margin_pct
```

If any stored realized or variance value disagrees with recomputation, semantic validation MUST fail.

## Non-Attempted Outcome Invariant

```text
execution_status = not_attempted
    → realized_revenue_usd = 0
    → settlement_status = none
```

This invariant is represented in the outcome JSON Schema and MUST also be enforced by the semantic evaluator.

## Scoreboard Boundary

`AGENT_PNL_SCOREBOARD_V0_1` is downstream and out of scope for this package.

A future scoreboard may aggregate only validated decision and realized-outcome receipts. It may recompute totals and ratios; it may not invent revenue, cost, profit, settlement, authority, or execution state.

```text
EVERY COST → RECEIPT
EVERY REVENUE → RECEIPT
EVERY PROFIT CLAIM → RECOMPUTABLE
NO RECEIPT → NO COMMERCIAL TRUTH CLAIM
```
