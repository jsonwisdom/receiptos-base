# RP-005 Notes

- Profile A (RFC 8785 JCS)
- Classified families: valid/, invalid/, edge/, regression/
- Rejection diagnostics use exit code 65
- replay_id fields use deterministic UUIDv7 placeholders
- Conformance contract frozen in metadata/CONFORMANCE.md (v1.0.0)
- root_hash bound: 3811d6961928668b7b780ab3c248e66dd318b23c66c2ba4b1d2dc7d037de722b
- digests.json records per-file SHA-256 used for root computation
- Verification bundle checklist: metadata/VERIFICATION_BUNDLE_CHECKLIST.md
- State: WAITING_FOR_RECEIPTS until Team A/B VerificationResult + CE-2 are present
- Legacy vectors/ placeholders are outside the sealed set and ignored by root_hash
