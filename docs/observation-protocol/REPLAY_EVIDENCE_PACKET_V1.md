# Replay Evidence Packet V1

Status: draft implementation for Issue #90.
Authority: false.

## Purpose

A Replay Evidence Packet bundles captures, annotations, raw payload hashes, manifest checks, and validation output into a single reviewable packet.

The packet is not a truth claim. It is an auditable container for evidence, limitations, and test results.

## Packet layout

Recommended directory structure:

```text
packet_demo_PKT-747-002-0001/
  packet_manifest.json
  raw/
    raw_payload_001.txt
  captures/
    capture_001.json
  annotations/
    annotation_001.json
```

## Required packet manifest fields

```json
{
  "packet_id": "PKT-747-002-0001",
  "authority": false,
  "captures": ["captures/capture_001.json"],
  "annotations": ["annotations/annotation_001.json"],
  "raw_payloads": [
    {
      "path": "raw/raw_payload_001.txt",
      "sha256": "..."
    }
  ],
  "created_at_utc": "2026-07-06T00:00:00Z"
}
```

## Validation gates

### Gate 1: schema validation

Validate capture and annotation documents against:

- `schemas/observation/CAPTURE_SCHEMA_V1.json`
- `schemas/observation/ANNOTATION_SCHEMA_V1.json`

Gate 1 requires real JSON Schema validation. Fallback mode is not sufficient for certification.

### Gate 2: packet lint

Cross-file checks:

- Raw payload hashes match files.
- Every annotation references existing capture IDs.
- `authority` is false.
- No high-confidence claim is promoted from an unconfirmed mutable field without limitation.
- Manifest paths resolve.

## Positive certification target

A positive packet must pass both gates and exit `0`.

Expected terminal receipt:

```text
PASS - positive packet passes
```

## Negative certification targets

The negative harness must reject:

1. Tampered raw payload.
2. Missing `capture_id` reference.
3. `authority:true`.
4. `observed:false` with non-null `value`.
5. Extra `notes` field in capture.
6. Empty `referenced_capture_ids`.

Expected terminal receipt:

```text
PASS - tampered raw payload fails
PASS - missing capture_id fails
PASS - authority:true fails
PASS - observed:false with value fails
PASS - capture notes field fails
PASS - empty referenced_capture_ids fails
```

## Certification bar

The packet is eligible for protocol certification only when the harness reports:

```text
7/7 checks passed.
CERTIFICATION PASSED. Eligible for validation log + tag.
Exit code: 0
```

## Tag rule

`observation-protocol-v1` must point to a commit that contains:

- protocol definitions
- schemas
- validator
- negative harness
- packet fixture or generated fixtures
- `VALIDATION_LOG.md` with pasted output and exit code

No tag may be cut from scaffold-only files or narrated success.
