# PR 47 Additive Core Review Manifest

## Status

review_only: true  
production_apply: false  
authority: false  
truth_claim: false  
mutation: false

## Purpose

This document defines the allowed additive scope for PR #47 after PR #45 and PR #46.

PR #47 is a review artifact only. It must not apply Supabase migrations, alter production schema, or redefine existing tables.

## Prior Chain

- PR #45 merged: MCP call receipt review draft originated.
- PR #46 merged: review SQL moved out of `supabase/migrations` into `docs/sql-review`.

## Allowed Scope

PR #47 may propose additive surrounding topology only:

- `wave_metadata`
- `asset_registry`
- `observational_receipts`

These structures may reference or orbit the ReceiptOS asset model, but must not redefine `public.mcp_call_receipts`.

## Prohibited Scope

PR #47 must not:

- modify `supabase/migrations/**`
- redefine `public.mcp_call_receipts`
- alter existing review SQL from PR #45 except by separate explicit review
- introduce production migration execution
- introduce authority escalation
- introduce truth-claim semantics

## Governance Invariants

```text
authority=false
truth_claim=false
mutation=false
production_apply=false
review_only=true
```

## Merge Gate

Before merge, verify changed files contain only review documentation under `docs/sql-review/` unless a separate explicit review authorizes otherwise.

No Supabase apply occurs from this PR.
