# Conformance Report – v1.0.0

Issue: #34

## ESG-001 Base Specification – v1.0.0

ReceiptOS / ESG-001 is locked as a representation protocol.

## Boundaries enforced

- `authority=false` / `truth_claim=false`: no inference, no truth adjudication.
- `artifact_hash` is treated as an opaque cryptographic claim when present in application profiles.
- Base frame `payload_hash` binds the canonical frame payload bytes.
- `signature` is an envelope object with `key_id`, `signature_bytes`, and optional `profile`.
- Signature algorithm and key format remain profile-defined.
- Validator is stateless and shape-only at the base layer.
- Production timestamp skew defaults to ±300 seconds.
- `--disable-timestamp` exists only for deterministic fixture and CI replay.

## Relevant commits

- `dace40916469968216cee32dea5f703d64adba19` — defer artifact hash canonicalization to profiles.
- `10d14db5b09d77111f21e3b8c0fbcbe4f756df4c` — document pluggable signature profiles.
- `c1916fe3ef7f596ebed4b12e60526379ccf222f9` — schema signature envelope object.
- `843dcfa5cce270b694b798a5eaaaf01ef6b3cc90` — validator envelope-shape check only.
- `2d07ee654af0ec73267015ae50c340fd4a7703a7` — RP-001 fixture signature envelope.
- `991850d99af791754921d7e88a785a1a64dfc7d7` — deterministic timestamp bypass for fixtures.

## Canonical conformance command

```bash
python tools/validate_receiptos_frame.py fixtures/rp-001-receiptos-frame.example.json --disable-timestamp
```

## Expected result

```json
{
  "authority": false,
  "conformant": true,
  "errors": [],
  "hash_match": true,
  "nonce_well_formed": true,
  "signature_envelope_valid": true,
  "timestamp_check_disabled": true,
  "timestamp_within_bounds": true,
  "truth_claim": false,
  "valid_encoding": true
}
```

## Conformance checks

- Schema: `schemas/receiptos-frame.schema.json` defines strict base frame shape.
- Validator: `tools/validate_receiptos_frame.py` validates base representation boundaries only.
- Fixture: `fixtures/rp-001-receiptos-frame.example.json` is structurally valid and timestamp-bypassable for deterministic CI.
- Statelessness: validator holds zero cache and requires zero external state.
- Replay protection: production mode enforces bounded timestamp skew by default.
- Signature: validator rejects malformed base64 shape, requires `key_id`, and ignores crypto-policy semantics.

## Non-goals

The base conformance validator does not perform:

- truth adjudication
- legal classification
- causation inference
- confidence promotion
- graph-derived state mutation
- artifact hash canonicalization for profile-specific artifacts
- curve-specific or key-format-specific signature verification
- shared-state replay registry checks

## Tagging commands

Use these commands from a clean local checkout after pulling this commit:

```bash
git tag -a v1.0.0 -m "ESG-001 Base Spec: Representation Protocol lock"
git push origin v1.0.0
```

## Release notes

```markdown
## ESG-001 Base Specification – v1.0.0 (Representation Protocol Lock)

**Boundaries enforced:**
- `authority=false` / `truth_claim=false` – no inference, no truth adjudication.
- `artifact_hash` treated as opaque cryptographic claim when defined by an application profile.
- `signature` as envelope object (`key_id` + `signature_bytes` + optional `profile`) – crypto-policy-neutral.
- Validator is stateless, shape-only, with ±300s production skew and `--disable-timestamp` for deterministic CI.

**Commits:**
- `dace409` – hash opacity
- `10d14db` – crypto-neutrality
- `c1916fe`–`2d07ee` – envelope schema/validator/fixture
- `991850d` – green path + skew handling

**Conformance:**
Run `python tools/validate_receiptos_frame.py fixtures/rp-001-receiptos-frame.example.json --disable-timestamp` → conformant.
```
