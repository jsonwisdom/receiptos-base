# PRC-JRN Curriculum v1.1

**Status:** Operational  
**Framework:** PRC-JRN Framework v1.x  
**Mode:** Validation-backed curriculum  
**Authority:** Educational framework for structured inquiry, not a truth oracle.

PRC-JRN teaches a repeatable inquiry habit: observe carefully, separate observations from assessments, document what changed, and revise when better evidence appears.

---

## 1. Constitution Anchor

The Constitution is frozen for the v1.x series. Field receipts may improve curriculum, facilitator guidance, and examples. They do **not** modify the Constitution.

```text
Observation != Assessment
Questions before conclusions.
Verification before confidence.
Evidence updates assessments.
Revision is a strength.
Unknowns define the perimeter of the audit.
```

**Constitution SHA-256:** `63bef9d6e3906d34a44a6ea2b1212cb13cc26aed94cadff7acd880b3f664afb2`

---

## 2. Receipts Machine Engine

The Engine is invariant for the v1.x series.

```text
Question
  ↓
Source
  ↓
Evidence
  ↓
Replay / Reproducibility
  ↓
Assessment
  ↓
Revision
```

**Engine SHA-256:** `90fe8c4d010acbc8883af840920014595799d24efb25d8fa191b8e261e043c8d`

The Receipts Machine does not determine truth. It provides a disciplined process for evaluating claims as evidence changes. Observations are documented, assessments are provisional, and revision is expected when better evidence appears.

---

## 3. Curriculum v1.1 Cases

| Case | Domain / Failure Mode | Core Distinction | Claim Template |
|---|---|---|---|
| 001 | Markets / attention | Attention != Evidence | "This new token will 100x by next month." |
| 002 | Science / headlines | Headline != Research | "A new study changes everything." |
| 003 | Breaking news / speed | Speed != Verification | "Something huge is happening right now." |
| 004 | Media / synthetic or decontextualized artifacts | Media Quality != Evidence Quality | "The video shows exactly what happened." |
| 005 | Framing / context collapse | Accurate Fact != Complete Context | "The quote is real, so the claim is true." |
| 006 | Causation / post-hoc reasoning | Correlation != Causation | "After Policy X was introduced, Event Y increased. Therefore, Policy X caused Event Y." |

---

## 4. Case 001 — The Viral Investment

**Core distinction:** Attention != Evidence

**Receipts Machine prompts:**

- What is the original source of the prediction?
- What evidence supports the projection?
- Is there independent analysis?
- What historical comparisons are relevant?
- What would falsify the claim?

**Validation target:** Participants separate market attention from evidentiary support.

---

## 5. Case 002 — The Scientific Breakthrough

**Core distinction:** Headline != Research

**Receipts Machine prompts:**

- Where is the original paper?
- Has it been peer reviewed?
- Are methods and data available?
- Has the result been independently replicated?
- What limitations did the authors state?

**Validation target:** Participants separate headlines, press releases, papers, and replicated evidence.

---

## 6. Case 003 — The Breaking News Story

**Core distinction:** Speed != Verification

**Receipts Machine prompts:**

- What is the original source?
- What is confirmed?
- What is still unknown?
- Is there independent corroboration?
- What evidence would update the assessment?

**Validation targets:** Participants resist urgency bias and distinguish repetition from corroboration.

**Known curriculum deltas from validation:**

- Add urgency-as-trigger module.
- Add source-lineage micro-exercise.

---

## 7. Case 004 — The High-Fidelity Illusion

**Core distinction:** Media Quality != Evidence Quality

**Standing rule:** Resolution measures media quality. Provenance measures evidentiary quality.

**Receipts Machine prompts:**

- Can the file be traced to the raw capture source?
- Is metadata available or stripped?
- Is chain of custody documented?
- Does the context match public records?
- Has independent verification occurred?

**Validation target:** Participants distinguish media quality from evidence quality before reaching an assessment.

---

## 8. Case 005 — Context Collapse

**Core distinction:** Accurate Fact != Complete Context

**Standing rule:** Facts require context. Context requires receipts.

**Receipts Machine prompts:**

- Is the original source located?
- Is the full surrounding context available?
- What material omissions may exist?
- Does interpretation go beyond the evidence?
- What additional context would change the assessment?

**Validation target:** Participants distinguish accurate excerpts from complete evidentiary context.

---

## 9. Case 006 — Causation Mirage

**Core distinction:** Correlation != Causation

**Standing rule:** Two events occurring together do not, by themselves, establish that one caused the other.

**Receipts Machine prompts:**

- Is the original dataset available?
- Is temporal sequence verified?
- Are alternative explanations considered?
- Is there a comparison group?
- Is there causal evidence or only circumstantial evidence?

**Validation target:** Participants separate sequence from causation and request causal receipts.

---

## 10. Standard Field Receipt

Each validation session should produce a receipt using the schema in:

```text
modules/prc-jrn/receipt.schema.json
```

Minimum fields:

- `receipt_id`
- `framework_version`
- `case_id`
- `claim_reviewed`
- `baseline_assessment`
- `final_assessment`
- `observed_behaviors`
- `curriculum_delta`
- `constitution_changes_proposed`
- `engine_changes_proposed`

Expected for v1.x:

```text
constitution_changes_proposed: []
engine_changes_proposed: []
```

---

## 11. Stewardship Rule

Every custodian inherits three responsibilities:

1. Preserve the Constitution.
2. Apply the Engine faithfully.
3. Improve the Curriculum only through documented observation.

Curriculum may evolve. Artifacts may evolve. The v1.x Constitution and Engine do not drift.
