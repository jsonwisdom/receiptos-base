# ACTIVE_LANES v2 Constitutional Boundary

GREEN means: receipt verified, hash matches, replay succeeds, authority=false.
GREEN does not mean: the underlying claim is true.

Timestamp, not tribunal.

This boundary is load-bearing. ACTIVE_LANES records provenance and replay status, not truth authority. Downstream lanes inherit this invariant by default.

LANE: AL
STATUS: GREEN
STATUS_SOURCE: VERIFIED_RECEIPT
RECEIPT_PTR: sha256:22b00da22b00da22b00da22b00da22b00da22b00da22b00da22b00da22b00da
authority: false

LANE: CWaaS
STATUS: YELLOW
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: false

LANE: PRC-JRN-EXT-001
STATUS: YELLOW
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: false
