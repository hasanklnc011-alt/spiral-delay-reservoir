import hashlib,json,unittest
from pathlib import Path
P6_ROOT=Path(__file__).resolve().parents[1]
class G3CouplerTests(unittest.TestCase):
    def test_remote_mode_section_is_converged_and_hash_locked(self):
        r=json.loads((P6_ROOT/"runs"/"g3c-coupler-mode-result-v1.json").read_text(encoding="utf-8"));self.assertTrue(r["mode_gate_passed"]);self.assertLess(r["center_length_relative_mesh_delta"],.01)
        for x in r["results"]:
            self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/x["result_file"]).read_bytes()).hexdigest(),x["result_sha256"])
    def test_transition_fdtd_fails_closed(self):
        for name in ("g3c-coupler-fdtd-result-v1.json","g3c-coupler-fdtd-result-v2.json"):
            r=json.loads((P6_ROOT/"runs"/name).read_text(encoding="utf-8"));self.assertFalse(r["pilot_passed"]);self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/r["result_file"]).read_bytes()).hexdigest(),r["result_sha256"])
    def test_y_splitter_and_mmi_sweep_fail_closed(self):
        y=json.loads((P6_ROOT/"runs"/"g3c-y-splitter-result-v1.json").read_text(encoding="utf-8"))
        self.assertFalse(y["pilot_passed"])
        self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/y["result_file"]).read_bytes()).hexdigest(),y["result_sha256"])
        m=json.loads((P6_ROOT/"runs"/"g3c-mmi-sweep-result-v1.json").read_text(encoding="utf-8"))
        self.assertFalse(m["sweep_passed"]);self.assertIsNone(m["selected_length_um"])
        self.assertEqual(len(m["results"]),5)
        for x in m["results"]:
            self.assertFalse(x["passed"])
            self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/x["result_file"]).read_bytes()).hexdigest(),x["result_sha256"])
    def test_targeted_mmi_mode_screen_and_fdtd_fail_closed(self):
        screen=json.loads((P6_ROOT/"runs"/"g3cd-mmi-mode-screen-result-v1.json").read_text(encoding="utf-8"))
        self.assertTrue(screen["screen_passed"]);self.assertFalse(screen["cloud_called"])
        self.assertLess(next(x for x in screen["mesh_convergence"] if x["mmi_width_um"]==2.0)["relative_fundamental_branch_beat_mesh_delta"],.005)
        self.assertEqual(hashlib.sha256((P6_ROOT/"g3_mmi_mode_screen.py").read_bytes()).hexdigest(),screen["source_sha256"])
        result=json.loads((P6_ROOT/"runs"/"g3cd-mmi-targeted-result-v1.json").read_text(encoding="utf-8"))
        self.assertFalse(result["suite_passed"]);self.assertIsNone(result["selected_length_um"])
        for x in result["results"]:
            self.assertFalse(x["passed"])
            self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/x["result_file"]).read_bytes()).hexdigest(),x["result_sha256"])
    def test_slot_y_builder_bug_is_separate_from_valid_v2_rejection(self):
        invalid=json.loads((P6_ROOT/"runs"/"g3c-slot-y-result-v1.json").read_text(encoding="utf-8"));self.assertFalse(invalid["evidence_valid"]);self.assertFalse(invalid["physical_candidate_evaluated"])
        valid=json.loads((P6_ROOT/"runs"/"g3c-slot-y-result-v2.json").read_text(encoding="utf-8"));self.assertTrue(valid["evidence_valid"]);self.assertTrue(valid["symmetry_invariant_passed"]);self.assertFalse(valid["pilot_passed"]);self.assertFalse(valid["solve_restarted"])
        self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/valid["result_file"]).read_bytes()).hexdigest(),valid["result_sha256"])
        self.assertEqual(hashlib.sha256((P6_ROOT/"g3_slot_y_postprocess_v2.py").read_bytes()).hexdigest(),valid["postprocessor_sha256"])
    def test_long_slot_y_and_taper_diagnostic_fail_closed(self):
        long=json.loads((P6_ROOT/"runs"/"g3c-slot-y-result-v3.json").read_text(encoding="utf-8"));self.assertFalse(long["pilot_passed"]);self.assertGreater(long["final_decay"],1e-7);self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/long["result_file"]).read_bytes()).hexdigest(),long["result_sha256"])
        taper=json.loads((P6_ROOT/"runs"/"g3c-slot-y-taper-result-v1.json").read_text(encoding="utf-8"));self.assertFalse(taper["taper_passed"]);self.assertTrue(taper["reflection_evidence_valid"]);self.assertFalse(taper["output_power_evidence_valid"]);self.assertGreater(taper["metrics"]["center_reflection_db"],-30)
    def test_union_y_is_hash_locked_and_fails_closed(self):
        estimate=json.loads((P6_ROOT/"runs"/"g3c-union-y-estimate-v1.json").read_text(encoding="utf-8"));result=json.loads((P6_ROOT/"runs"/"g3c-union-y-result-v1.json").read_text(encoding="utf-8"))
        self.assertFalse(estimate["solve_started"]);self.assertLess(estimate["estimated_flexcredits"],0.5);self.assertEqual(estimate["task_id"],result["task_id"])
        self.assertEqual(hashlib.sha256((P6_ROOT/"g3_union_y_splitter.py").read_bytes()).hexdigest(),result["source_sha256"]);self.assertEqual(hashlib.sha256((P6_ROOT/"runs"/result["result_file"]).read_bytes()).hexdigest(),result["result_sha256"])
        self.assertFalse(result["pilot_passed"]);self.assertGreater(result["metrics"]["center_excess_loss_db"],0.2);self.assertGreater(result["metrics"]["worst_reflection_db"],-30);self.assertGreater(result["metrics"]["max_abs_energy_residual"],0.01);self.assertGreater(result["final_decay"],1e-7)
    def test_cloud_sources_require_cost_and_solve_approval(self):
        for name in ("g3_coupler_remote.py","g3_coupler_fdtd.py","g3_coupler_fdtd_v2.py","g3_y_splitter_fdtd.py","g3_mmi_sweep.py","g3_mmi_targeted.py","g3_slot_y_splitter.py","g3_slot_y_splitter_v2.py","g3_slot_y_splitter_v3.py","g3_slot_y_taper_diagnostic.py","g3_union_y_splitter.py"):
            s=(P6_ROOT/name).read_text(encoding="utf-8");self.assertIn("user-credit-approval",s);self.assertIn("user-solve-approval",s)
if __name__=="__main__":unittest.main()
