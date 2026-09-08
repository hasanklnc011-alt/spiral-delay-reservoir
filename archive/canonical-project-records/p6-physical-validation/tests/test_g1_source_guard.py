import hashlib
import json
import unittest
from pathlib import Path


P6_ROOT = Path(__file__).resolve().parents[1]


class P6G1SourceGuardTests(unittest.TestCase):
    def test_g1_solver_has_no_cloud_calls(self):
        source = (P6_ROOT / "g1_mode_solver.py").read_text(encoding="utf-8")
        forbidden = ["tidy3d" + ".web", "web" + ".run", "web" + ".upload", "estimate" + "_cost"]
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_g1_solver_pins_exact_tidy3d_version(self):
        source = (P6_ROOT / "g1_mode_solver.py").read_text(encoding="utf-8")
        self.assertIn('REQUIRED_TIDY3D_VERSION = "2.12.0"', source)

    def test_remote_preflight_is_serialization_only(self):
        source = (P6_ROOT / "g1_remote_preflight.py").read_text(encoding="utf-8")
        forbidden = ["tidy3d" + ".web", "web" + ".run", "web" + ".upload", "estimate" + "_cost"]
        for token in forbidden:
            self.assertNotIn(token, source)
        self.assertIn('"cloud_called": False', source)
        self.assertIn('"cost_estimate_status": "BLOCKED_UNTIL_USER_CREDIT_APPROVAL_AND_UPLOAD"', source)

    def test_remote_preflight_record_is_hash_bound_and_no_spend(self):
        record = json.loads(
            (P6_ROOT / "runs" / "g1-remote-subpixel-preflight-v1.json").read_text(encoding="utf-8")
        )
        source_hash = hashlib.sha256((P6_ROOT / "g1_remote_preflight.py").read_bytes()).hexdigest()
        config_hash = hashlib.sha256((P6_ROOT / "configs" / "baseline-v1.json").read_bytes()).hexdigest()
        self.assertEqual(record["source_sha256"], source_hash)
        self.assertEqual(record["config_sha256"], config_hash)
        self.assertEqual(record["frequency_count"], 13)
        self.assertTrue(record["subpixel_spec_present"])
        self.assertFalse(record["cloud_called"])
        self.assertFalse(record["upload_allowed"])
        self.assertFalse(record["solve_allowed"])
        self.assertTrue(record["passed"])

    def test_cloud_gate_can_only_upload_and_estimate(self):
        source = (P6_ROOT / "g1_cloud_gate.py").read_text(encoding="utf-8")
        self.assertIn("--user-credit-approval", source)
        self.assertIn("--task-id", source)
        self.assertIn("job.upload()", source)
        self.assertIn("job.estimate_cost", source)
        self.assertNotIn("job.start(", source)
        self.assertNotIn("job.run(", source)
        self.assertIn('"solve_started": False', source)

    def test_upload_estimate_record_is_hash_bound_and_unsolved(self):
        record = json.loads((P6_ROOT / "runs" / "g1-upload-estimate-v1.json").read_text(encoding="utf-8"))
        source_hash = hashlib.sha256((P6_ROOT / "g1_cloud_gate.py").read_bytes()).hexdigest()
        self.assertEqual(record["cloud_gate_source_sha256"], source_hash)
        self.assertEqual(record["task_status"], "draft")
        self.assertLess(record["estimated_flexcredits"], record["pilot_flexcredit_limit"])
        self.assertTrue(record["within_pilot_limit"])
        self.assertFalse(record["solve_started"])

    def test_g1_executor_is_approval_and_task_lock_guarded(self):
        source = (P6_ROOT / "g1_execute.py").read_text(encoding="utf-8")
        self.assertIn("--user-solve-approval", source)
        self.assertIn('record["task_id"]', source)
        self.assertIn('record["within_pilot_limit"]', source)
        self.assertIn("task_id_cached=task_id", source)
        self.assertNotIn("web.run(", source)

    def test_first_remote_result_is_hash_bound_and_failed_closed(self):
        record = json.loads((P6_ROOT / "runs" / "g1-remote-subpixel-result-v1.json").read_text(encoding="utf-8"))
        source_hash = hashlib.sha256((P6_ROOT / "g1_execute.py").read_bytes()).hexdigest()
        result_hash = hashlib.sha256((P6_ROOT / "runs" / record["result_file"]).read_bytes()).hexdigest()
        self.assertEqual(record["executor_source_sha256"], source_hash)
        self.assertEqual(record["result_sha256"], result_hash)
        self.assertEqual(record["task_status"], "success")
        self.assertEqual(record["analysis"]["guided_te_like_mode_count"], 1)
        self.assertFalse(record["analysis"]["group_index_and_delay_gate_passed"])
        self.assertFalse(record["g1_nominal_passed"])

    def test_candidate_probe_has_no_cloud_path(self):
        source = (P6_ROOT / "g1_candidate_probe.py").read_text(encoding="utf-8")
        for token in ("tidy3d" + ".web", "web" + ".run", "web" + ".upload"):
            self.assertNotIn(token, source)
        self.assertIn('"cloud_called": False', source)

    def test_candidate_batch_is_cost_and_approval_guarded(self):
        source = (P6_ROOT / "g1_candidate_batch.py").read_text(encoding="utf-8")
        self.assertIn("PILOT_TOTAL_LIMIT_FC = 0.5", source)
        self.assertIn("--user-credit-approval", source)
        self.assertIn("--user-solve-approval", source)
        self.assertIn('record["within_pilot_limit"]', source)
        self.assertIn("task_id_cached=item[\"task_id\"]", source)

    def test_selected_validation_covers_mesh_and_fabrication_corners(self):
        source = (P6_ROOT / "g1_selected_validation.py").read_text(encoding="utf-8")
        for name in ("nominal_m15", "nominal_m20", "nominal_m25", "width_low", "width_high", "height_low", "height_high"):
            self.assertIn(name, source)
        self.assertIn("relative_n_group_delta", source)
        self.assertIn("absolute_n_eff_delta", source)
        self.assertIn("fabrication_corners_passed", source)

    def test_g1_acceptance_is_backed_by_convergence_and_hdf5_hashes(self):
        accepted = json.loads((P6_ROOT / "configs" / "g1-accepted-v1.json").read_text(encoding="utf-8"))
        selected = json.loads((P6_ROOT / "runs" / "g1-selected-validation-result-v1.json").read_text(encoding="utf-8"))
        thickness = json.loads((P6_ROOT / "runs" / "g1-thickness-refinement-result-v1.json").read_text(encoding="utf-8"))
        self.assertTrue(selected["convergence"]["passed"])
        self.assertTrue(selected["nominal_passed"])
        self.assertTrue(selected["width_plus_minus_10nm_passed"])
        self.assertFalse(selected["height_plus_minus_10nm_passed"])
        self.assertTrue(thickness["thickness_plus_minus_5nm_passed"])
        self.assertTrue(accepted["g1_passed"])
        evidence_items = [selected["nominal"], selected["width_low"], selected["width_high"], selected["height_low"], selected["height_high"], *thickness["results"]]
        for item in evidence_items:
            actual = hashlib.sha256((P6_ROOT / "runs" / item["result_file"]).read_bytes()).hexdigest()
            self.assertEqual(item["result_sha256"], actual)

    def test_latest_local_run_is_hash_bound_and_failed_closed(self):
        record = json.loads((P6_ROOT / "runs" / "g1-local-seed-v2.json").read_text(encoding="utf-8"))
        source_hash = hashlib.sha256((P6_ROOT / "g1_mode_solver.py").read_bytes()).hexdigest()
        config_hash = hashlib.sha256((P6_ROOT / "configs" / "baseline-v1.json").read_bytes()).hexdigest()
        self.assertEqual(record["source_sha256"], source_hash)
        self.assertEqual(record["config_sha256"], config_hash)
        self.assertEqual(record["tidy3d_version"], "2.12.0")
        self.assertFalse(record["cloud_called"])
        self.assertFalse(record["g1_passed"])
        self.assertFalse(record["fine_mesh_delay_mapping"]["delay_gate_passed"])


if __name__ == "__main__":
    unittest.main()
