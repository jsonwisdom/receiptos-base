# Lesson 027 Sequence Editor View v0.1

Witness-only iOS UI surface for Before / During / After sequencing.

Authority: false.
No fake green.
Dumb view only.
Binding pass-through only.
Structural buckets only.
No causal inference.
No diagnosis.
No PTSD conclusion.
No cognitive impairment label.
No symptom tracker claim.
No clinical inference.
No medical conclusion.
No legal conclusion.
No benefits prediction.
No rating estimate.
No eligibility claim.
No service-connection conclusion.
No VA outcome prediction.
No telemetry.
No services.
No runtime certification claim.

## Source Scope

LESSONS_010_TO_026_LOCKED.

## Purpose

Lesson 027 adds a minimal SequenceEditorView surface.

The view accepts three SwiftUI bindings:

- beforeText
- duringText
- afterText

The view only organizes user-entered text into temporal buckets.

Before / During / After are structure aids, not evidence judgments.

## Allowed

- local text editing
- @Binding pass-through
- temporal organization
- before bucket
- during bucket
- after bucket
- safe boundary copy

## Blocked

- causation claim
- diagnosis
- PTSD conclusion
- cognitive impairment label
- symptom tracker claim
- clinical inference
- medical conclusion
- legal conclusion
- credibility judgment
- benefits prediction
- rating estimate
- eligibility claim
- service-connection conclusion
- VA outcome prediction
- telemetry
- network call
- hidden transform
- scoring
- pattern-as-proof

## Safe Copy

Allowed:

- Organize what happened.
- These are structure buckets only.
- Nothing here decides cause or outcome.
- You can revise any bucket before locking a receipt.

Blocked:

- This caused your condition.
- This proves PTSD.
- This supports service connection.
- This weakens your claim.
- This determines eligibility.
- This predicts a rating.

## Final State

SequenceEditorView is a faithful dumb temporal scaffold only.
