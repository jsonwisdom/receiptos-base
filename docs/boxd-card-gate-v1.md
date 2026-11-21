# BoxD CI-FIRST card gate (draft)

No card is release-approved based on artistic appearance or a crop count. This guard **fails closed** when the output is not a portrait PNG, smaller than 750 × 1050, lacks SHA-256 bindings, quotes words not found in the locked source, or falsely asserts audio verification.

Command:
```bash
python tools/boxd_card_gate.py --image card.png --manifest card.json --transcript Trump_2026-11-20_VERIFIED_BASELINE.txt --report card.audit.json
```
Exit code 0 = PASS. Exit code 1 = FAIL or HOLD. Never add cards to a release ZIP when exit code is 1.

Expected manifest fields:
```json
{
  "card_id": "BBP-001",
  "image_sha256": "<actual sha256>",
  "transcript_sha256": "<actual sha256>",
  "quote": "<exact publisher-transcript substring>",
  "audio_status": "UNVERIFIED",
  "uniqueness_attested": false,
  "concept_set_hash": null,
  "independent_visual_inspection": null
}
```

Rules:
- Existing originals remain unchanged in BoxD.
- Metadata fields are *not* self-authenticating. Independent inspection must check full border, typography, one dominant character/gag, exact rendered lettering, and absence of duplicate concept. If no inspector is integrated, those checks stay HOLD. A metadata field saying PASS alone is not proof.
- The detector is a **structural gate**, not a certified collage or border vision classifier. It rejects the supplied 1536x1024 ten-panel sheet because of its landscape geometry; it does not infer that every portrait image contains exactly one card.
- The quote match is text-only. It does not establish that Trump spoke the quote on audio or at a precise second. A genuine audio receipt is required for audio verification.
- Do not fabricate verification stamps, QR destinations, timestamps, citations, or a green badge inside artwork.
- A checked manifest cannot retroactively approve flawed artwork.
- This branch is a proposed gate, not proof that a GitHub Actions workflow is deployed or that all fifty cards exist.

**Known sample failure**: user-provided sheet 1536 × 1024, ten panels; gate requires ONE_PORTRAIT_CARD and MIN_750x1050, so it must FAIL.

## Failure-to-rule feedback contract (V2)

This section supersedes the previous practice of delivering a failure spreadsheet to the operator.

Each failed or unknown check must produce an output containing `remediation.policy_id`,
`remediation.failed_rules[].rule_id`, `remediation.failed_rules[].action`,
`remediation.machine_action`, and `remediation.human_triage_required=false`.

Rules are version-controlled in `rules/boxd-card-failure-rules-v2.json`.
Known defects are associated with specific deterministic correction instructions;
unknown defects must create a **proposed** rule plus a regression in a draft PR
before code may ever treat them as accepted. Machine-derived proposals require CI
and provenance; never silently rewrite a released standard.

Factory state machine:
```
OBSERVE FAILURE
  -> PRESERVE ARTIFACT + HASH + RECEIPT
  -> MAP RULE ID (or DRAFT NEW RULE)
  -> MACHINE REPAIR/RERENDER (at most 3 attempts)
  -> AUTOMATED INDEPENDENT REINSPECTION
  -> PASS if ALL checks PASS
  -> otherwise HOLD, with failed attempts preserved
```

**Important implementation boundary**: the current CLI identifies and *emits*
the machine remediation instructions, and regression tests enforce their
classification. It does NOT autonomously invoke an image renderer, open new PRs,
or use a true independent vision inspector yet. These absent execution layers
must remain HOLD. Do not tell the human to visually certify each card.

The rejected 10-panel sheet now has explicit R001 and R002 rules. The invented
quotations and false VERIFIED badges have R003 and R004 rules. New occurrences
must trip the same gates without operator intervention.
