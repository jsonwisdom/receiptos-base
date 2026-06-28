import hashlib
import json
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECEIPT = REPO / "evidence/receipts/global-forest-verification.json"

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

class ReceiptDeterminism(unittest.TestCase):
    def run_verify(self):
        r = subprocess.run(
            ["python3", "tools/verify_global_forest.py"],
            cwd=REPO,
            text=True,
            capture_output=True
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(RECEIPT.exists())

    def test_receipt_determinism_and_semantics(self):
        self.run_verify()
        a = RECEIPT.read_bytes()
        ah = hashlib.sha256(a).hexdigest()

        self.run_verify()
        b = RECEIPT.read_bytes()
        bh = hashlib.sha256(b).hexdigest()

        self.assertEqual(a, b)
        self.assertEqual(ah, bh)

        receipt = json.loads(b)
        self.assertEqual(receipt["authority"], False)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["algorithm"], "sha256")
        self.assertEqual(receipt["manifest_path"], "global-manifest.json")
        self.assertEqual(receipt["verifier"], "tools/verify_global_forest.py")
        self.assertEqual(receipt["verifier_version"], "1.0")
        self.assertRegex(receipt["global_root"], r"^0x[0-9a-f]{64}$")
        self.assertRegex(receipt["manifest_hash"], r"^0x[0-9a-f]{64}$")

        manifest = json.loads((REPO / "global-manifest.json").read_text())
        expected_manifest_hash = "0x" + hashlib.sha256(canonical(manifest)).hexdigest()
        self.assertEqual(receipt["manifest_hash"], expected_manifest_hash)

if __name__ == "__main__":
    unittest.main()
