import ast
import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "g3d_mmi_eme_width_screen.py"


class G3DEMEWidthScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.text)

    def test_screen_is_narrow_and_physics_guided(self):
        self.assertIn("WIDTHS_UM = (1.2, 1.4)", self.text)
        self.assertIn("local mode diagnosis", self.text)
        self.assertNotIn("P5_RESULTS", self.text)

    def test_preflight_has_no_cloud_action(self):
        function = next(
            node for node in self.tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "preflight"
        )
        calls = {
            getattr(node.func, "attr", getattr(node.func, "id", ""))
            for node in ast.walk(function) if isinstance(node, ast.Call)
        }
        self.assertFalse({"upload", "run", "estimate_cost"} & calls)

    def test_paid_paths_are_approval_and_hash_guarded(self):
        self.assertIn('if not approved:', self.text)
        self.assertIn('Source changed after estimate', self.text)
        self.assertIn('Locked simulation mismatch', self.text)
        self.assertIn('locked["within_limits"]', self.text)

    def test_eme_cannot_accept_g3d(self):
        self.assertIn('"g3d_accepted": False', self.text)
        self.assertIn("requires broadband two-source FDTD", self.text)

    def test_saved_records_remain_blind_safe_when_present(self):
        for name in (
            "g3d-mmi-eme-width-preflight-v1.json",
            "g3d-mmi-eme-width-estimate-v1.json",
            "g3d-mmi-eme-width-screen-result-v1.json",
        ):
            path = HERE / "runs" / name
            if path.exists():
                record = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(record.get("p5_blind_rerun", False))

    def test_completed_screen_is_hash_locked_and_fails_closed(self):
        result_path = HERE / "runs" / "g3d-mmi-eme-width-screen-result-v1.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(
            result["source_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        )
        estimate = HERE / "runs" / "g3d-mmi-eme-width-estimate-v1.json"
        self.assertEqual(
            result["estimate_sha256"], hashlib.sha256(estimate.read_bytes()).hexdigest()
        )
        for task in result["tasks"]:
            path = HERE / "runs" / task["result_file"]
            self.assertEqual(
                task["result_sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
            )
            self.assertEqual(task["task_status"], "success")
        self.assertFalse(result["screen_passed"])
        self.assertFalse(result["g3d_accepted"])


if __name__ == "__main__":
    unittest.main()
