import hashlib
import json
import unittest
from pathlib import Path


P6_ROOT = Path(__file__).resolve().parents[1]


class G3StraightSourceGuardTests(unittest.TestCase):
    def test_preflight_has_no_cloud_path_and_two_lengths(self):
        source = (P6_ROOT / "g3_straight_preflight.py").read_text(encoding="utf-8")
        for token in ("tidy3d" + ".web", "web" + ".run", "web" + ".upload"):
            self.assertNotIn(token, source)
        self.assertIn("for length in (4.0, 8.0)", source)
        self.assertIn("subpixel=True", source)
        self.assertIn('"cloud_called": False', source)

    def test_cloud_execution_is_cost_and_task_guarded(self):
        source = (P6_ROOT / "g3_straight_cloud.py").read_text(encoding="utf-8")
        self.assertIn("PER_SOURCE_LIMIT_FC = 0.5", source)
        self.assertIn("TOTAL_LIMIT_FC = 3.0", source)
        self.assertIn("--user-credit-approval", source)
        self.assertIn("--user-solve-approval", source)
        self.assertIn("task_id_cached=item[\"task_id\"]", source)

    def test_v2_separates_scattering_from_propagation_loss(self):
        preflight = (P6_ROOT / "g3_straight_preflight_v2.py").read_text(encoding="utf-8")
        cloud = (P6_ROOT / "g3_straight_cloud_v2.py").read_text(encoding="utf-8")
        self.assertIn("lossless equivalent for component scattering", preflight)
        self.assertIn("propagation loss external", cloud)
        self.assertIn("task_id_cached=item[\"task_id\"]", cloud)

    def test_v2_accepted_evidence_is_hash_locked(self):
        record = json.loads(
            (P6_ROOT / "runs" / "g3a-straight-lossless-result-v2.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(record["g3a_passed"])
        self.assertIn("propagation loss external", record["material_policy"])
        self.assertEqual(len(record["results"]), 4)
        for result in record["results"]:
            payload = (P6_ROOT / "runs" / result["result_file"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), result["result_sha256"])
        self.assertTrue(all(item["passed"] for item in record["convergence"].values()))


if __name__ == "__main__":
    unittest.main()
