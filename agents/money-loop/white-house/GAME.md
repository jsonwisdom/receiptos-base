# White House Replay Arena v0.1

A deterministic evidence-replay game for testing whether a White House characterization package survives mechanical scrutiny.

## Constitutional rule

```text
SCORE != TRUTH
WIN != GUILT
BADGE != AUTHORITY
REPLAY_READY != CLAIM_TRUE
```

The arena scores **audit mechanics only**. It cannot award points for political agreement, accusation strength, guilt, intent, deception, misconduct, or legal conclusions.

## Seven mechanic points

A round can earn one point for each replayable condition:

1. `SOURCE_POINTER_BOUND`
2. `SOURCE_BYTES_REPLAYED`
3. `IDENTITY_PROVENANCE_REPLAYED`
4. `DELTA_CLASSIFIED`
5. `SEMANTIC_RENDERING_BOUNDED`
6. `EXACT_HEAD_EXECUTED`
7. `BYPASS_SURFACES_BLOCKED`

All seven yields `REPLAY_READY`. Anything less yields `HOLD`.

`REPLAY_READY` means the mechanical packet is ready for human review. It does not mean the White House claim, DOJ record, allegation, or interpretation is true.

## Surface gauntlet

T16 must survive four presentation paths independently:

```text
JSON
CLI
REPORT
LOG
```

Each path routes through the same typed semantic renderer. A widening attempt such as `Fraud proven`, `Claim proven`, `Guilt established`, or `Legal finding` must fail before the surface emits output.

## External source rule

Public White House bytes remain outside the arena until exact-head CI and the four-surface gauntlet are green.

```text
PUBLICATION_EXISTS != CONTENT_CORROBORATED
OFFICIAL_HOST != OFFICIAL_FINDING
BYTES_PRESERVED != SOURCE_AUTHENTIC
```

## Authority

```text
authority_created = false
```

Always.
