# Dependency Remediation — 2026-08-01

**Status:** `DRAFT_SECURITY_RAIL`  
**Authority:** `FALSE`  
**Promotion:** `NONE`  
**Canonicalization PR coupling:** `NONE`

## Scope

This rail adds exact npm overrides for the two transitive packages reported by GitHub Actions:

```text
postcss = 8.5.23
sharp   = 0.35.3
```

The existing `next` major line is not downgraded or force-replaced. GitHub Actions must demonstrate that installation, audit, build, and package checks remain valid.

## Excluded

- no `npm audit fix --force`;
- no Next.js major migration;
- no canonicalization-profile change;
- no validator-CI repair;
- no release or deployment action;
- no audit closure;
- no merge authorization.
