import sys
import unittest
from pathlib import Path


P6_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P6_ROOT))

from em_plan import REQUIRED_TIDY3D_VERSION, budget_policy, selected_cases, validate_plan  # noqa: E402


class P6EmPlanTests(unittest.TestCase):
    def test_exact_tidy3d_version_is_pinned(self):
        self.assertEqual(REQUIRED_TIDY3D_VERSION, "2.12.0")

    def test_mode_gate_precedes_paid_component_fdtd(self):
        cases = {case["case"]: case for case in selected_cases()}
        self.assertEqual(cases["cross_section_mode"]["depends_on"], [])
        for name in ("straight_deembedding", "bend_90deg", "adjacent_spiral_turn_coupling", "progressive_signal_tap", "lo_1x2_splitter", "coherent_2x2_mmi"):
            self.assertIn("cross_section_mode", cases[name]["depends_on"])

    def test_all_cloud_jobs_start_unsubmitted(self):
        for case in selected_cases():
            self.assertIn(case["cloud_status"], {"NOT_SUBMITTED", "NOT_APPLICABLE_UNTIL_PDK_DEFINED"})

    def test_full_length_fdtd_is_not_in_plan(self):
        names = {case["case"] for case in selected_cases()}
        self.assertNotIn("full_14cm_fdtd", names)

    def test_progressive_tap_and_lo_splitter_have_distinct_metrics(self):
        cases = {case["case"]: case for case in selected_cases()}
        self.assertIn("target_kappa_power_absolute_error_max", cases["progressive_signal_tap"]["acceptance"])
        self.assertNotIn("imbalance_db_max", cases["progressive_signal_tap"]["acceptance"])
        self.assertEqual(cases["lo_1x2_splitter"]["acceptance"]["target_kappa_power"], 0.5)
        self.assertIn("imbalance_db_max", cases["lo_1x2_splitter"]["acceptance"])

    def test_cost_and_approval_gate_is_machine_enforced(self):
        policy = budget_policy()
        self.assertFalse(policy["user_credit_approval"])
        self.assertFalse(policy["upload_allowed"])
        self.assertFalse(policy["solve_allowed"])
        self.assertTrue(validate_plan()["passed"])

    def test_convergence_thresholds_are_consistent(self):
        cases = {case["case"]: case for case in selected_cases()}
        for name in ("straight_deembedding", "bend_90deg", "progressive_signal_tap", "lo_1x2_splitter", "coherent_2x2_mmi"):
            acceptance = cases[name]["acceptance"]
            self.assertEqual(acceptance["mesh_loss_delta_db_max"], 0.02)
            self.assertEqual(acceptance["mesh_phase_delta_deg_max"], 0.5)


if __name__ == "__main__":
    unittest.main()
