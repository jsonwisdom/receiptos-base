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
