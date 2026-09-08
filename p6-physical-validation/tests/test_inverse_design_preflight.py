import ast
import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "inverse_design_preflight.py"
CONFIG = HERE / "configs" / "inverse-design-v1.json"
RESULT = HERE / "runs" / "inverse-design-id0-preflight-v1.json"


class InverseDesignPreflightTests(unittest.TestCase):
    def test_preflight_has_no_cloud_calls(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        attrs = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertFalse({"upload", "run", "estimate_cost"} & attrs)

    def test_config_keeps_devices_separate_and_blind_closed(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertFalse(config["p5_blind_rerun"])
        self.assertEqual(set(config["devices"]), {"g3c_splitter", "g3d_combiner"})
        self.assertEqual(
            config["devices"]["g3d_combiner"]["independent_sources"], 2
        )
        self.assertTrue(
            all(device["cannot_directly_accept"] for device in config["devices"].values())
        )

    def test_saved_preflight_is_hash_locked_and_non_accepting(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            result["source_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        )
        self.assertEqual(
            result["config_sha256"], hashlib.sha256(CONFIG.read_bytes()).hexdigest()
        )
        self.assertTrue(result["preflight_passed"])
        self.assertFalse(result["cloud_called"])
        self.assertFalse(result["id0_can_accept_device"])


if __name__ == "__main__":
    unittest.main()
