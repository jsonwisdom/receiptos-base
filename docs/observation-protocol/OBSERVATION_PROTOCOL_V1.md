# Observation Protocol V1

Status: draft implementation for Issue #90.
Authority: false.

## Purpose

Observation Protocol V1 separates mechanical capture from human or AI interpretation. Its core rule is simple: a system state claim is not promoted merely because it sounds plausible. It must be captured, checked, and classified.

This protocol exists to prevent the exact failure mode where a report about an external system is treated as fact before independent verification.

## Core separation

### Capture

A capture is a mechanical record of what was observed from a specified source at a specified time. Capture files may include only data fields and provenance needed to reproduce or audit the observation.

Capture records must not contain narrative, theory, intent, adoption claims, market interpretation, or institutional framing.

### Annotation

An annotation is commentary about one or more captures. It may contain hypotheses, limitations, interpretations, discrepancies, or predictions, but it must reference at least one capture.

Annotations cannot stand alone.

### Packet

A replay evidence packet bundles captures, annotations, raw payload hashes, a manifest, and validation output into one reviewable unit.

## Field replay classes

Every captured field must declare one replay class:

| Class | Meaning |
|---|---|
| `immutable` | Field should remain verifiable indefinitely, such as tx hash, contract address, block hash. |
| `point_in_time` | Field may change after capture, such as balance, holders, displayed metadata, transaction count. |
| `derived` | Field is computed from captured data, not directly fetched. |
| `annotation_ref` | Field points to a separate annotation record and is not itself analysis. |

Mutable or changing fields must not be represented as forever-replayable facts.

## Promotion path

| Stage | Allowed content | Required evidence |
|---|---|---|
| Capture | Mechanical observation + provenance | Source, timestamp, raw payload hash, field replay classes |
| Confirmed observation | Same field reproduced independently | Second source or observer; discrepancy handling if mismatch |
| Analytical claim | Interpretation or hypothesis | Capture references, confidence, prediction or limitation, authority false |

No analytical claim may be promoted from a single unconfirmed mutable field without an explicit limitation.

## Raw payload rule

A capture summary is not enough. The raw payload must be archived or represented by a content hash.

Required:

- `raw_payload_sha256`
- `source_type`
- `source_url_or_endpoint`
- `capture_timestamp_utc`
- `observer_id`
- `capture_method`

## Dual-source rule

For mutable fields, independent confirmation is required before a claim can be promoted above capture level.

A capture may record `confirmed_by: []` while pending. That is not a schema violation. It becomes a promotion violation if a high-confidence annotation relies on that unconfirmed mutable field without limitation.

## Authority rule

All records in this protocol must carry `authority: false` where applicable. The protocol records evidence and validation state; it does not grant truth authority.

## Forbidden in capture records

Capture records must not include:

- `notes`
- `interpretation`
- `hypothesis`
- `intent`
- `adoption_claim`
- `market_claim`
- `attention_vector`
- court or docket framing as evidence

These belong, if used at all, in annotation records.

## Authorship and attribution note

This protocol was developed through AI-assisted analysis and human verification. Claims, captures, repository mutations, and validation results require independent confirmation before being treated as evidence.

## Certification rule

The tag `observation-protocol-v1` must not be cut until:

1. Protocol files contain substantive definitions.
2. JSON schemas validate in full mode with `jsonschema` installed.
3. Positive packet passes.
4. Negative fixtures fail as expected.
5. `VALIDATION_LOG.md` contains the exact terminal output and exit code.
6. Git commit and tag references are independently observable.
