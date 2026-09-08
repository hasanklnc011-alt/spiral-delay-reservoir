import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


class PDKSelectionTests(unittest.TestCase):
    def test_selection_gate_is_fail_closed_and_blind_safe(self):
        record = json.loads(
            (HERE / "configs" / "pdk-selection-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(record["status"], "SELECTED_CUSTOM_PROCESS")
        self.assertEqual(
            record["decision"]["selected_path"],
            "retain_343x180_and_require_custom_process_evidence",
        )
        self.assertFalse(record["decision"]["reopen_g1_to_g3"])
        self.assertFalse(record["p5_blind_rerun"])
        self.assertFalse(record["public_evidence_sufficient_for_g4_acceptance"])
        self.assertFalse(record["g4_physical_accepted"])
        self.assertFalse(record["g5_composition_complete"])

    def test_220nm_candidates_reopen_the_locked_180nm_gate(self):
        record = json.loads(
            (HERE / "configs" / "pdk-selection-v1.json").read_text(encoding="utf-8")
        )
        for key in ("imec_isipp50g", "tower_ph18"):
            candidate = record["candidates"][key]
            self.assertEqual(candidate["public_si_thickness_um"], 0.22)
            self.assertEqual(candidate["result"], "REOPEN_G1_IF_SELECTED")


if __name__ == "__main__":
    unittest.main()
