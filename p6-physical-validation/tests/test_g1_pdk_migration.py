import ast
import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "g1_pdk_migration_probe.py"
RESULT = HERE / "runs" / "g1-220nm-pdk-migration-local-probe-v1.json"


class G1PDKMigrationProbeTests(unittest.TestCase):
    def test_probe_has_no_cloud_path(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        names = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        }
        self.assertNotIn("web", names)

    def test_saved_probe_is_hash_locked_and_cannot_accept_migration(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            result["source_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        )
        self.assertFalse(result["p5_blind_rerun"])
        self.assertFalse(result["cloud_called"])
        self.assertFalse(result["local_convergence_passed"])
        self.assertFalse(result["migration_g1_accepted"])
        self.assertEqual(result["height_um"], 0.22)


if __name__ == "__main__":
    unittest.main()
