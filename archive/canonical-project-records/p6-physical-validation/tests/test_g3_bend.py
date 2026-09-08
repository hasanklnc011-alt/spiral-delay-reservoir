import hashlib
import json
import unittest
from pathlib import Path


P6_ROOT = Path(__file__).resolve().parents[1]


class G3BendSourceGuardTests(unittest.TestCase):
    def test_preflight_is_local_and_covers_locked_screen(self):
        source = (P6_ROOT / "g3_bend_preflight.py").read_text(encoding="utf-8")
        for token in ("tidy3d" + ".web", "web" + ".run", "web" + ".upload"):
            self.assertNotIn(token, source)
        self.assertIn("RADII_UM = (10.0, 20.0, 30.0, 50.0)", source)
        self.assertIn("PITCH_UM = 5.0", source)
        self.assertIn('"cloud_called": False', source)

    def test_bend_uses_accepted_g1_and_lossless_scattering_policy(self):
        source = (P6_ROOT / "g3_bend_preflight.py").read_text(encoding="utf-8")
        self.assertIn("G1_CONFIG", source)
        self.assertIn("lossless_materials", source)
        self.assertIn("fabricated propagation loss external", source)

    def test_cloud_execution_is_cost_and_task_guarded(self):
        source = (P6_ROOT / "g3_bend_cloud.py").read_text(encoding="utf-8")
        self.assertIn("PER_SOURCE_LIMIT_FC", source)
        self.assertIn("--user-credit-approval", source)
        self.assertIn("--user-solve-approval", source)
        self.assertIn('task_id_cached=locked["task_id"]', source)

    def test_accepted_bend_is_fine_mesh_and_hash_locked(self):
        result = json.loads((P6_ROOT / "runs" / "g3b-bend-r10-deembedded-fine-convergence-v1.json").read_text(encoding="utf-8"))
        self.assertTrue(result["g3b_bend_passed"])
        self.assertLess(result["convergence"]["deembedded_phase_delta_deg"], 0.5)
        record = json.loads((P6_ROOT / "runs" / "g3b-bend-r10-m25-convergence-result-v2.json").read_text(encoding="utf-8"))
        payload = (P6_ROOT / "runs" / record["result_file"]).read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), record["result_sha256"])

    def test_adjacent_turn_bound_passes_at_selected_pitch(self):
        result = json.loads((P6_ROOT / "runs" / "g3b-adjacent-turn-supermode-v2.json").read_text(encoding="utf-8"))
        self.assertTrue(result["passed"])
        self.assertEqual(result["selected_pitch_um"], 5.0)
        self.assertLess(result["selected_worst_crosstalk_db"], -30.0)


if __name__ == "__main__":
    unittest.main()
