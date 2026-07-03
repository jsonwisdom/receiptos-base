# Docket #57 — Authorized Identity Gate

## Status

BOUND TO ROS-0006

## Binding

Docket #57 binds the ReceiptOS identity-binding gate to:

```text
ROS-0006: Authorized Identity Invariant
```

No identity binding SHALL be considered valid unless it is proven against the Authorized Identity through the canonical path for that identity type.

## Authorized Identity

```text
jaywisdom.base.eth
0xA380552a27b0a5a2874Ea7AA52CAC09f542002E8
```

## Identity Type

```text
contract account
```

## Canonical Verification Path

```text
ERC-1271 isValidSignature(hash, signature)
```

Required magic value:

```text
0x1626ba7e
```

## Non-Canonical Path For This Docket

EIP-191 remains canonical for EOAs, but it is not forced onto this docket because the Authorized Identity is a contract account.

The system MUST NOT pretend the Authorized Identity is an EOA.

## Boundary

The docket preserves:

```json
{
  "verdict": "WITNESS_ONLY",
  "authority": false,
  "truth_claim": false
}
```

## State

```text
RECEIPTOS_WIRE_WORKFLOW_SUCCESS
ROS-0006_ACTIVE
DOCKET_57_BOUND
```
