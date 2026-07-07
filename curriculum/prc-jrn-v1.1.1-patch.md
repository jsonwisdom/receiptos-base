# PRC-JRN Curriculum v1.1.1 Patch

**Status:** Patch queued from public validation receipts  
**Framework:** PRC-JRN-v1.1  
**Patch Type:** Curriculum hardening only  
**Authority:** false

This patch does not modify the PRC-JRN Constitution or Engine. It hardens curriculum guidance based on EXT-002 and EXT-003 public validation receipts.

---

## Source Receipts

| Receipt | Case | Signal | Result |
|---|---:|---|---|
| PRC-JRN-FIELD-EXT-002 | 002 | Echo consensus / source-lineage collapse | insufficient_evidence |
| PRC-JRN-FIELD-EXT-003 | 004 | High-fidelity illusion / custody void | insufficient_evidence |

---

## Case 002 Hardening

Add a source-lineage checklist:

- Independent origin verification required.
- Trace compression to a single root source must be flagged.
- Echo consensus across outlets is not independent corroboration.
- Multiple citations that all inherit the same claim path count as one lineage until independently verified.

**Patch rule:**

```text
multiple_sources && single_origin && !independent_verification -> insufficient_evidence
```

---

## Case 004 Hardening

Add a provenance/custody checklist:

- Metadata review required for high-fidelity media.
- Chain of custody required before evidentiary promotion.
- Synthetic or edited-media risk must be considered when fidelity is used as persuasive force.
- Missing custody chain defaults to advisory status only.

**Patch rule:**

```text
high_fidelity_media && !custody_chain -> insufficient_evidence
```

---

## Global Ingestion Note

High signal is not high proof.

Repetition, visual polish, resolution, and production quality are trust proxies. PRC-JRN treats them as prompts for inquiry, not as evidence conclusions.

---

## Stewardship

```text
constitution_changes_proposed: []
engine_changes_proposed: []
authority: false
```

This patch strengthens examples, checklists, and intake gates only. It does not change the constitutional layer or the invariant Receipts Machine Engine.
