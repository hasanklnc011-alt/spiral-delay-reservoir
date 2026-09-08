import inspect
import hashlib
import json
import unittest
from pathlib import Path

import g3d_mmi_fdtd as g3d


class G3DMMISourceTests(unittest.TestCase):
    def test_preflight_is_two_source_no_cloud_and_blind_safe(self):
        record = g3d.preflight()
        self.assertTrue(record["preflight_passed"])
        self.assertFalse(record["cloud_called"])
        self.assertFalse(record["p5_blind_rerun"])
        self.assertEqual(record["independent_excitations"], ["upper", "lower"])
        self.assertFalse(record["upload_allowed"])
        self.assertFalse(record["solve_allowed"])

    def test_geometry_is_scaled_from_official_seed_and_has_distinct_ports(self):
        geometry = g3d.geometry_parameters()
        self.assertAlmostEqual(geometry["waveguide_width_um"], 0.343)
        self.assertAlmostEqual(geometry["waveguide_height_um"], 0.18)
        self.assertGreater(geometry["near_guide_gap_um"], 0)
        self.assertGreater(
            geometry["far_port_center_um"], geometry["near_port_center_um"]
        )

    def test_paid_paths_require_explicit_flags_and_locked_task_ids(self):
        source = inspect.getsource(g3d)
        self.assertIn("User credit approval required", source)
        self.assertIn("User solve approval required", source)
        self.assertIn("task_id_cached=item[\"task_id\"]", source)
        self.assertIn("Source changed after estimate", source)

    def test_acceptance_is_fail_closed_at_m15(self):
        source = inspect.getsource(g3d.execute)
        self.assertIn('"g3d_accepted": False', source)
        self.assertIn("m20/m25 convergence", source)
        self.assertIn('"passive_singular_value_le_1p000001"', source)

    def test_saved_pilot_is_two_source_hash_locked_and_rejected(self):
        root = Path(__file__).resolve().parents[1]
        result = json.loads((root / "runs" / "g3d-mmi-result-v1.json").read_text(encoding="utf-8"))
        self.assertFalse(result["p5_blind_rerun"])
        self.assertFalse(result["pilot_passed"])
        self.assertEqual(len(result["tasks"]), 2)
        for task in result["tasks"]:
            path = root / "runs" / task["result_file"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), task["result_sha256"])
        self.assertGreater(result["metrics"]["worst_imbalance_db"], 0.5)
        self.assertGreater(result["metrics"]["worst_excess_insertion_loss_db"], 1.5)


if __name__ == "__main__":
    unittest.main()
