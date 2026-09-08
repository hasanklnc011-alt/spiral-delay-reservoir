import hashlib
import json
import unittest
from pathlib import Path

from g5_composition import build_g5_record


class G5CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = build_g5_record()

    def test_accepted_gates_are_composed_but_open_evidence_fails_closed(self):
        gates = self.record["gates"]
        for name in ("g1_group_index", "g2_layout", "g3a_straight_reference", "g3b_bend"):
            self.assertEqual(gates[name], "PASS")
        self.assertFalse(self.record["g5_composition_complete"])
        self.assertFalse(self.record["p6_accepted"])

    def test_delay_loss_assumption_is_not_mislabeled_as_physical_evidence(self):
        delay = self.record["delay_path"]
        self.assertTrue(delay["assumption_within_stress_limit"])
        self.assertEqual(delay["physical_evidence_status"], "OPEN_UNTIL_PROPAGATION_PDK_OR_CUTBACK")

    def test_blind_is_not_rerun(self):
        self.assertFalse(self.record["p5_blind_rerun"])

    def test_saved_record_and_inputs_are_hash_locked(self):
        root = Path(__file__).resolve().parents[1]
        saved = json.loads((root / "runs" / "g5-composition-result-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, self.record)
        self.assertEqual(saved["source_sha256"], hashlib.sha256((root / "g5_composition.py").read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
