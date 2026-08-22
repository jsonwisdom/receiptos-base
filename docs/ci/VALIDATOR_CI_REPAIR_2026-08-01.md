# Validator CI Repair — 2026-08-01

**Status:** `DRAFT_REPAIR_RAIL`  
**Authority:** `FALSE`  
**Promotion:** `NONE`  
**Canonicalization PR coupling:** `NONE`

## Scope

This rail only:

1. restores `ci/scripts/run_lint.sh` as an executable validator preflight;
2. adds a read-only repair workflow;
3. sets `permissions: read-all`;
4. sets `persist-credentials: false`;
5. runs the existing Python test suite after preflight.

The restored script performs syntax, importability, and existing canonical-rail smoke checks. It does not claim a broader lint contract than it executes.

## Excluded

- no canonicalization-profile change;
- no dependency remediation;
- no release or deployment action;
- no audit closure;
- no merge authorization;
- no authority activation.
