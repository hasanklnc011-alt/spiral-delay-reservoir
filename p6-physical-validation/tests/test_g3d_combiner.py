import hashlib
import json
import unittest
from pathlib import Path

from g3d_combiner_reuse_diagnostic import build_record


ROOT = Path(__file__).resolve().parents[1]


class G3DCombinerDiagnosticTests(unittest.TestCase):
    def test_reuse_is_no_cloud_and_cannot_accept_g3d(self):
        record = build_record()
        self.assertFalse(record["cloud_called"])
        self.assertFalse(record["p5_blind_rerun"])
        self.assertFalse(record["g3d_accepted"])
        self.assertFalse(record["gates"]["independent_two_port_excitations"])
        self.assertFalse(record["gates"]["mesh_convergence_available"])

    def test_saved_record_is_hash_locked_and_fail_closed(self):
        saved = json.loads(
            (ROOT / "runs" / "g3d-reused-coupler-diagnostic-v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(saved, build_record())
        self.assertEqual(
            saved["source_sha256"],
            hashlib.sha256((ROOT / "g3d_combiner_reuse_diagnostic.py").read_bytes()).hexdigest(),
        )
        self.assertFalse(saved["diagnostic_passed"])
        self.assertGreater(saved["quadrature_error_deg"], 5.0)
        self.assertGreater(saved["largest_total_power_operator_eigenvalue"], 1.01)


if __name__ == "__main__":
    unittest.main()
