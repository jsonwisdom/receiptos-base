#!/usr/bin/env python3
import json
from pathlib import Path

RECEIPT_PATH = Path("receipts/mru-001-minimal-replay-unit.json")

receipt = json.loads(RECEIPT_PATH.read_text())

print("WHY EXISTS:", receipt["artifact_id"])
print("Subject:", receipt["subject"])
print("Source:", receipt["source_artifact"]["path"])
print("SHA256:", receipt["source_artifact"]["sha256"])
print("State:", receipt["evidence_state"])
print("Edge:", receipt["provenance_edges"][0]["type"])
print("Justification:", receipt["provenance_edges"][0]["justification"])
print("authority:", receipt["authority"])
print("truth_claim:", receipt["truth_claim"])
