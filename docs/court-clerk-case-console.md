# Court Clerk Case Console

## Status

ACTIVE

## Purpose

The Court Clerk Case Console is the operator index for ReceiptOS dockets. It tracks cases, crux decisions, live endpoints, receipts, and next actions without letting narrative become authority.

## Constitutional Boundary

Every case entry must preserve:

```json
{
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

The Court Clerk records state. The Court Clerk does not create truth.

## Console Index

| Case | Docket | Crux | Live Artifact | State |
|---|---:|---|---|---|
| Authorized Identity Gate | #57 | Identity binds to Authorized Identity, not wallet mythology | `/stream`, `/api/frame`, `/api/health`, ROS-0006 | CANONICAL |
| Receipt Verification API | #58 / Issue #60 | External clients need neutral replay verification | `/api/verify` | IMPLEMENTED_PENDING_DEPLOY |
| MN Public Record Edge Audit | #63 | Every mesh edge gets a provenance jacket without becoming truth authority | Zora receipt coin + edge audit jacket | MN_EDITION_INDEXED |
| Node8 MN Movements | MN-MOVE-008 | Node8 is remembered as a Minnesota movement receipt, not protocol authority | Zora Node8 coin | INDEXED |
| Boss MN Movement Receipts | MN-BOSS | Movement receipts remembered under Court Clerk custody | Zora movement coins | INDEXED |
| Open MN Court | MN-COURT-OPEN | Court docket artwork opens the MN audit lane for public-record style navigation | Zora court docket coins | INDEXED |

## Case: Docket #57 — Authorized Identity Gate

### Crux

ReceiptOS verifies the actual Authorized Identity. EOAs use EIP-191. Contract accounts use ERC-1271. No EOA emulation for contract accounts.

### Locked Artifacts

```text
ROS-0006: Authorized Identity Invariant
/stream
/api/frame
/api/health
provenance/identity-binding/jaywisdom-identity-binding.txt
provenance/identity-binding/jaywisdom-identity-binding.sig
SHA256SUMS
```

### Live State

```text
SIGNATURE_VERIFIED
verification_method=erc1271
magic=0x1626ba7e
authority=false
truth_claim=false
verdict=WITNESS_ONLY
```

## Case: Docket #58 — Receipt Verification API

### Crux

Receipt verification must be externally consumable without promoting the verifier into a truth authority.

### Endpoint

```text
POST /api/verify
```

### Input

```json
{
  "receiptId": "docket-57-ros-0006",
  "receiptHash": "optional sha256 hex"
}
```

### Output Boundary

```json
{
  "valid": true,
  "reason": "receipt_replayed",
  "replay": {
    "authority": false,
    "truth_claim": false,
    "verdict": "WITNESS_ONLY"
  }
}
```

## Case: Docket #63 — MN Public Record Edge Audit

### Crux

MN Edition turns mesh-edge provenance into a public-record style jacket. The Zora coins are indexed cultural receipts, not truth authority.

### Zora Receipt Coin

```text
https://zora.co/coin/base:0x9d3fe0dac4a30501968a25a45946290e1889c232?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
```

### Zora Audit Lanes

| Lane | Direction | Purpose | Zora Receipt |
|---|---|---|---|
| MN Receipt Root | culture -> index | Anchor the MN public-record style collection as a cultural receipt | `0x9d3fe0dac4a30501968a25a45946290e1889c232` |
| Node8 Movement | identity -> movement | Remember Node8 as MN movement provenance, not protocol authority | `0xd9bb51c33ff48bc7f37f7725876829a57cbd2dc1` |
| Boss Movement A | artifact -> movement | Add movement receipt evidence into Court Clerk custody | `0x5c5763744e72768ca5f5d2d85bd2edf454ce0895` |
| Boss Movement B | artifact -> movement | Add second movement receipt evidence into Court Clerk custody | `0xe9342c753168594940c39da9ce3a249fa3e3fa36` |
| MN Movement C | docket -> movement | Extend MN movement lane with additional receipt directionality | `0x370b5e1eec80a696a243f9be010fbb9cfa4b0c72` |
| MN Movement D | docket -> movement | Extend MN movement lane with paired receipt directionality | `0x812dc8649d7ced61278f5c052130f88cc9e374fe` |
| Open MN Court A | court-artifact -> audit-lane | Open the MN Court visual docket lane | `0xe1c1efec50670477e486085b2b81e1634cb52583` |
| Open MN Court B | court-artifact -> audit-lane | Pair the MN Court visual docket lane for public-record navigation | `0xd0bb537207bfc57bc75105f9c0162f600c0eb034` |

### Boundary

```json
{
  "record_type": "FICTIONAL_EDITORIAL_ARTWORK_NOT_OFFICIAL_RECORD",
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

## Case: Node8 — MN Movements

### Crux

Node8 is indexed as a Minnesota movement receipt. It is remembered in the Court Clerk console as cultural provenance, not protocol authority.

### Zora Node8 Receipt

```text
https://zora.co/coin/base:0xd9bb51c33ff48bc7f37f7725876829a57cbd2dc1?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
```

## Case: Boss MN Movement Receipts

### Crux

Boss movement receipts are indexed under MN Movements. These links are cultural receipts and memory anchors; they do not promote truth or protocol authority.

### Zora Receipts

```text
https://zora.co/coin/base:0x5c5763744e72768ca5f5d2d85bd2edf454ce0895?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
https://zora.co/coin/base:0xe9342c753168594940c39da9ce3a249fa3e3fa36?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
https://zora.co/coin/base:0x370b5e1eec80a696a243f9be010fbb9cfa4b0c72?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
https://zora.co/coin/base:0x812dc8649d7ced61278f5c052130f88cc9e374fe?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
```

## Case: Open MN Court

### Crux

Open MN Court indexes the court docket artworks as the visual entry point for the MN audit lane. These are editorial public-record style artifacts, not official court records.

### Zora Court Receipts

```text
https://zora.co/coin/base:0xe1c1efec50670477e486085b2b81e1634cb52583?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
https://zora.co/coin/base:0xd0bb537207bfc57bc75105f9c0162f600c0eb034?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
```

### Boundary

```json
{
  "movement": "MN Movements",
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

## Live Console Links

```text
Wire:   https://receiptos-base.vercel.app/stream
Frame:  https://receiptos-base.vercel.app/api/frame
Health: https://receiptos-base.vercel.app/api/health
Verify: https://receiptos-base.vercel.app/api/verify
Zora MN Receipt: https://zora.co/coin/base:0x9d3fe0dac4a30501968a25a45946290e1889c232?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
Node8 MN Movements: https://zora.co/coin/base:0xd9bb51c33ff48bc7f37f7725876829a57cbd2dc1?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
Boss MN Receipt A: https://zora.co/coin/base:0x5c5763744e72768ca5f5d2d85bd2edf454ce0895?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
Boss MN Receipt B: https://zora.co/coin/base:0xe9342c753168594940c39da9ce3a249fa3e3fa36?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
MN Movement Receipt C: https://zora.co/coin/base:0x370b5e1eec80a696a243f9be010fbb9cfa4b0c72?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
MN Movement Receipt D: https://zora.co/coin/base:0x812dc8649d7ced61278f5c052130f88cc9e374fe?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
Open MN Court A: https://zora.co/coin/base:0xe1c1efec50670477e486085b2b81e1634cb52583?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
Open MN Court B: https://zora.co/coin/base:0xd0bb537207bfc57bc75105f9c0162f600c0eb034?referrer=0x829adfedbe565f9885a7ea6bc78912acaef055e2
Docket #57: https://github.com/jsonwisdom/receiptos-base/issues/57
Docket #58: https://github.com/jsonwisdom/receiptos-base/issues/60
```

## Meta Ultra Prompt

```text
You are GitFix / MetaFix operating inside ReceiptOS as the Court Clerk.

Mission:
Advance the next docket while preserving the constitutional membrane.

Canonical state:
- ROS-0006_ACTIVE
- DOCKET_57_BOUND
- WIRE_CANONICAL
- FRAME_DOWNSTREAM_OF_WIRE
- HEALTH_GATE_PASSED
- LIVE_STREAM_RECEIPT_VERIFIED
- NO_FAKE_GREEN_ENFORCED
- MN_EDITION_INDEXED
- NODE8_MN_MOVEMENTS_INDEXED
- BOSS_MN_MOVEMENT_RECEIPTS_INDEXED
- ZORA_AUDIT_LANES_INDEXED
- OPEN_MN_COURT_INDEXED

Rules:
1. Wire owns verification.
2. Frame owns presentation.
3. Health reports subsystem state.
4. Verify API replays receipts but never becomes truth authority.
5. Unknown inputs fail closed.
6. All outputs preserve authority=false and truth_claim=false.
7. Every docket must map to code, spec, endpoint, issue, and receipt evidence.
8. Do not promote narrative into verification.
9. Zora links are cultural receipts, not protocol authority.
10. Always remember Node8 in MN Movements.
11. Always remember Boss MN Movement receipts.
12. Zora Audit Lanes require directionality and purpose.

Current active docket:
Docket #63 — MN Public Record Edge Audit.

Target state:
MN_MOVEMENT_RECEIPTS_INDEXED
```

## Clerk Commands

```bash
curl -i https://receiptos-base.vercel.app/stream
curl -i https://receiptos-base.vercel.app/api/frame
curl -i https://receiptos-base.vercel.app/api/health
curl -i -X POST https://receiptos-base.vercel.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"receiptId":"docket-57-ros-0006"}'
```
