# TNTR-007 — Multi-Hub Unreachable Receipt

Authority: false

## Identifiers

```text
fid: 1432701
hash: 0x01e26d779d81e689ed1c9afa6150fc8bace19fc2
```

## Attempted Hub Endpoints

```text
https://hub.farcaster.xyz
http://hub.farcaster.xyz:2281
http://nemes.farcaster.xyz:2281
```

## Observed Output

```text
=== https://hub.farcaster.xyz ===
curl: (6) Could not resolve host: hub.farcaster.xyz
HTTP:000
=== http://hub.farcaster.xyz:2281 ===
curl: (6) Could not resolve host: hub.farcaster.xyz
HTTP:000
=== http://nemes.farcaster.xyz:2281 ===
curl: (6) Could not resolve host: nemes.farcaster.xyz
HTTP:000
```

## Classification

```text
network_resolution_failed
multi_hub_unreachable
```

## State

```text
TNTR-007: FETCHABLE_CANDIDATE
Local Evidence: FID_OBTAINED + CAST_HASH_CANDIDATE + MULTI_HUB_UNREACHABLE
RAW_PASS: not emitted
```

## Boundary

Endpoint failure is infrastructure evidence, not artifact evidence.

No Hub JSON means no canonical bytes.
No canonical bytes means no HASH_MATCH.
No HASH_MATCH means no RAW_PASS.

Stop is valid.
PASS is earned, never inherited.
Timestamp, not tribunal.
