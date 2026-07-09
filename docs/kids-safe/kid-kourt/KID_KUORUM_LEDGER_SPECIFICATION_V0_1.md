# Kid Kuorum Ledger Specification v0.1

Status: R&D_SAFE_EDUCATION  
Authority: false  
No fake green: true  
For: the children  
Surface: Kid Kuorum

## Definition

Kid Kuorum is a child-safety review threshold.

It is not a vote, not a majority mechanic, not a truth-decider, and not an authority surface.

Kid Kuorum requires enough review to keep children safe before Kid Kourt speaks.

## Required Four Surfaces

Every Kid Kourt ruling must include:

1. **Child question** — the initiating curiosity.
2. **Evidence or missing-evidence note** — what is known or not known.
3. **Safety boundary check** — how the child is protected.
4. **Repair or learning path** — how the situation can improve.

## Minimum Safe Circle

```text
1 claim
1 receipt
1 safety check
1 repair path
```

## Ledger Rule

No Kid Kourt ruling may be recorded as ready unless all four Kid Kuorum surfaces are present.

If any surface is missing, the ruling status must remain:

```text
KUORUM_INCOMPLETE / DO_NOT_RULE
```

## Valid Status Values

- `KUORUM_INCOMPLETE`
- `KUORUM_PRESENT`
- `READY_FOR_KID_KOURT_REVIEW`
- `RULING_RECORDED_R_AND_D_ONLY`

## Hard Boundaries

- Kid Kuorum does not grant authority.
- Kid Kuorum does not decide truth.
- Kid Kuorum does not permit child finance.
- Kid Kuorum does not permit child wallets.
- Kid Kuorum does not permit private data exposure.
- Kid Kuorum does not permit bullying or humiliation games.
- Kid Kuorum does not permit canonical promotion.

## Ruling

Kid Kuorum is the minimum child-safety participation invariant for Kid Kourt rulings.

Authority remains false.
