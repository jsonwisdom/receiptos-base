# Money Loop — Base Agentic Game v0.1

Status: `BUILD_CANDIDATE`  
Authority: `false`  
Real money enabled: `false`

Money Loop is a receipt-gated agentic game for testing whether automated content production can advance from an idea to **verified profit**.

It may use `harry0703/MoneyPrinterTurbo` as an external production adapter, but the producer is not the scoreboard.

## Core law

```text
VIDEO_CREATED != VIDEO_PUBLISHED
VIDEO_PUBLISHED != REVENUE_GENERATED
REVENUE_REPORTED != REVENUE_VERIFIED
REVENUE_VERIFIED - VERIFIED_COSTS = VERIFIED_PROFIT
```

No evidence, no promotion.

## State ladder

```text
IDEA
  -> ASSET_CREATED
  -> PUBLISHED
  -> SETTLEMENT_SEEN
  -> REVENUE_VERIFIED
  -> PROFIT_VERIFIED
```

`COST_VERIFIED` is a side transition and may be recorded before profit calculation.

## Agents

- **Scout** — proposes a topic, audience, offer, and distribution hypothesis.
- **Producer** — invokes an approved source/container production adapter and returns an artifact receipt.
- **Publisher** — publishes only with separately supplied platform authorization and returns a publication receipt.
- **Revenue Referee** — accepts a settlement/revenue observation but promotes money only from verified evidence.
- **Profit Keeper** — computes profit mechanically from verified revenue minus verified costs.

No agent receives authority merely because another agent completed a step.

## MoneyPrinterTurbo boundary

MoneyPrinterTurbo is optional external machinery. This repository does not vendor or execute its portable binary.

Production integration should:

1. pin an upstream commit or release;
2. run reviewed source or a controlled container;
3. inject secrets at runtime, never into game state or receipts;
4. bind the service to loopback/private networking unless independently protected;
5. hash the produced artifact;
6. hand only the artifact/evidence receipt into this game.

The upstream MIT software license does not prove rights to stock media, voices, music, generated output, or platform distribution.

## Evidence classes

Production events require evidence objects containing:

```json
{
  "ref": "provider-or-local-receipt-id",
  "kind": "artifact_sha256",
  "verified": true
}
```

Revenue promotion additionally requires `amount_cents` and verified settlement evidence. Profit is never accepted as an input claim; the engine computes it.

## Test mode

The genesis state has:

```text
production_runtime = false
real_money_enabled = false
```

Synthetic fixtures are allowed only in that mode and prove engine behavior, not income.

## Run

```bash
python agents/money-loop/selftest.py
```

A passing self-test establishes only deterministic game behavior.

```text
ENGINE_REPLAY_PASS != MONEY_MADE
AUTHORITY_CREATED = false
```
