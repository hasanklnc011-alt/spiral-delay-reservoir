import hashlib
import json
import unittest
from pathlib import Path

from g4_compact_validation import build_g4_record


class G4CompactValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = build_g4_record()

    def test_routing_is_10_pd_by_3_slots_and_requires_fast_switching(self):
        r = self.record["routing"]
        self.assertEqual((r["pd_count"], r["slot_count"]), (10, 3))
        self.assertEqual(r["slot_rate_hz"], 30e9)
        self.assertEqual(r["required_technology"], "fast_EO_or_switch")

    def test_thermal_is_static_only_and_evidence_stays_open(self):
        t = self.record["thermal"]
        self.assertLess(t["thermal_to_slot_rate_ratio"], 1e-6)
        self.assertAlmostEqual(t["average_heater_power_mw_assumption"], 395.0)
        self.assertAlmostEqual(t["maximum_heater_power_mw_assumption"], 770.0)
        self.assertEqual(t["maximum_headroom_mw_assumption"], 30.0)
        self.assertFalse(self.record["g4_physical_accepted"])

    def test_receiver_exposes_required_linearity_instead_of_claiming_it(self):
        receiver = self.record["receiver"]
        self.assertEqual(receiver["p5_compatibility_bandwidth_hz"], 50e9)
        self.assertAlmostEqual(receiver["required_linear_photocurrent_peak_a_at_responsivity_floor"], 0.0045)
        self.assertEqual(receiver["saturation_and_tia_swing_evidence"], "OPEN_PDK_OR_MEASUREMENT")

    def test_blind_is_not_rerun(self):
        self.assertFalse(self.record["p5_blind_rerun"])

    def test_saved_record_is_source_and_config_hash_locked(self):
        root = Path(__file__).resolve().parents[1]
        saved = json.loads((root / "runs" / "g4-compact-validation-result-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, self.record)
        self.assertEqual(saved["source_sha256"], hashlib.sha256((root / "g4_compact_validation.py").read_bytes()).hexdigest())
        self.assertEqual(saved["config_sha256"], hashlib.sha256((root / "configs" / "baseline-v1.json").read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
