# Free-Only Three-Surface Receipts

## Purpose

ReceiptOS Base can process receipts at machine speed only if each receipt declares exactly what evidence was observed and exactly what claims remain forbidden.

`FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2` is a narrow receipt type for Base-native replay evidence using free public RPC surfaces.

It is a witness receipt, not an authority receipt.

## Required surfaces

A receipt of this type must include all three observed surfaces:

```text
TX_RECEIPT_SURFACE=observed
LOG_SURFACE=observed
STATE_READ_SURFACE=observed
```

In JSON form:

```json
{
  "surfaces": {
    "tx_receipt": "observed",
    "log_surface": "observed",
    "state_read": "observed"
  }
}
```

## Boundary lock

Every receipt must carry:

```json
{
  "receipt_type": "FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2",
  "authority": false,
  "free_only": true,
  "no_fake_green": true,
  "trace": {
    "debug_traceTransaction": "not_used",
    "internal_calls_observed": false
  }
}
```

## Forbidden elevations

This receipt type must not claim:

- wallet control
- creator identity
- token authenticity
- legal ownership
- payment or sale semantics
- trace/internal call structure

The boundary object must keep those claims false:

```json
{
  "boundary": {
    "proves_internal_trace": false,
    "proves_wallet_control": false,
    "proves_creator_identity": false,
    "proves_token_authenticity": false,
    "proves_payment_or_sale": false,
    "proves_legal_ownership": false
  }
}
```

## What this enables

ReceiptOS Base can route receipts at machine speed:

```text
missing surface -> reject
trace used while free_only=true -> reject
authority=true -> reject
wallet/control/authenticity/payment claim -> reject
all boundaries intact -> admissible witness receipt
```

## Non-claims

A valid receipt proves only that the declared surfaces were observed.

It does not prove ownership, identity, authenticity, payment, sale, legality, or truth beyond the observed data.

## Verifier

Run:

```bash
python3 verifier/free_only_three_surface.py receipts/
```

or point it at specific receipt files:

```bash
python3 verifier/free_only_three_surface.py path/to/receipt.json
```

## Final boundary

```text
authority=false
free_only=true
no_fake_green=true
```
