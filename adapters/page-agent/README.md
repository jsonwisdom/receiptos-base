# ReceiptOS PageAgent Adapter

Status: test gate scaffold.

PageAgent acts. ReceiptOS proves. Replay decides.

This adapter keeps the UI action layer separate from the proof layer. The first gate verifies deterministic receipt capture before any release.

## Gate

- same command plus same DOM yields the same command hash and DOM-before hash
- DOM mutation records before and after hashes
- authority remains false
- replay compares expected DOM-after hash
