# Jay's GitHub Garbage Pail Kids Factory

**Project codename:** Agentic Topps Secret Project  
**Status:** TOOLING_DRAFT_V0_1  
**Authority:** false  
**Canon rule:** No receipt, no card.

This folder defines five GitHub-native Garbage Pail Kids factory agents. Each agent has a role, a membrane boundary, required inputs, outputs, and fail-closed behavior.

These agents do not create canon by vibe. They prepare artifacts for review, validation, hashing, and GitHub-walkable provenance.

## Factory Agents

| Agent | GPK Name | Role | Primary Output |
|---|---|---|---|
| `receipt-ricky` | Receipt Ricky | Evidence Intake | evidence packet |
| `canon-carrie` | Canon Carrie | Canon Gatekeeper | canon readiness report |
| `override-ollie` | Override Ollie | Quarantine / De-Canon | override or quarantine bundle |
| `lore-larry` | Lore Larry | Lore Continuity | lore drift report |
| `press-patty` | Press Patty | Card / Release Packaging | release-ready card packet |

## Shared Factory Invariants

1. **No unwitnessed state** — every card, joke, claim, and metadata field needs an evidence anchor.
2. **No silent mutation** — canon is never edited in place; it is superseded.
3. **CI before claims** — cards are drafts until validation passes.
4. **Receipts before narrative** — satire explains evidence, not the other way around.
5. **Authority false** — agents assist, they do not declare truth.
6. **GitHub-walkable provenance** — every output must point to commit, issue, PR, artifact, tag, or release.

## Operating Flow

```text
Receipt Ricky -> Canon Carrie -> Lore Larry -> Press Patty
                         |
                         v
                  Override Ollie
```

## Factory State

```text
AGENTS_DEFINED: true
CANON_MUTATION: false
REAL_CARD_TOUCHED: false
AUTHORITY: false
```

## Next Step

Run these agents against `gpk-card-test-001` only. Do not use real canon until the disposable test card passes intake, canon readiness, lineage check, quarantine, and override replay.
