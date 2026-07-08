"""
ReceiptOS canonical hash scaffold.

Status: scaffold only.
Issue: #119.

This file intentionally contains no passing implementation test yet.
The next implementation commit must replace this scaffold with a deterministic
JCS/RFC 8785 + Unicode NFC fixture test for Card 001.

Required future assertion:
- created_at / updated_at do not affect receipt_id
- variants do not affect receipt_id
- approval_status does not affect receipt_id
- receipt_id == keccak256(jcs(receipt_core))
"""
