import hashlib
import json
import unittest
from pathlib import Path

P6_ROOT=Path(__file__).resolve().parents[1]

class G2LayoutTests(unittest.TestCase):
    def setUp(self):
        self.result=json.loads((P6_ROOT/"runs"/"g2-spiral-layout-result-v1.json").read_text(encoding="utf-8"))
    def test_exact_length_radius_pitch_and_taps_pass(self):
        self.assertTrue(self.result["passed"])
        self.assertLess(self.result["relative_length_error"],.001)
        self.assertGreaterEqual(self.result["minimum_curvature_radius_um"],10.0)
        self.assertGreaterEqual(self.result["edge_gap_um"],self.result["minimum_drc_gap_um"])
        self.assertEqual(len(self.result["taps"]),20)
        self.assertAlmostEqual(self.result["predicted_total_delay_ps"],1906.1585653308287,places=6)
    def test_layout_artifacts_are_hash_locked(self):
        for name,digest in self.result["files"].items():
            payload=(P6_ROOT/"layout"/name).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(),digest)
        self.assertEqual((P6_ROOT/"layout"/"spiral-centerline-v1.gds").read_bytes()[:2],b"\x00\x06")
        self.assertEqual(self.result["gds"]["maximum_join_gap_um"],0.0)

if __name__=="__main__":unittest.main()
