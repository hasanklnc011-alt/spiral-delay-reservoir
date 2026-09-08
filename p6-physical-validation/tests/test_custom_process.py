import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


class CustomProcessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(
            (HERE / "configs" / "custom-process-validation-v1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_user_selected_cross_section_is_preserved(self):
        self.assertTrue(self.record["selected_by_user"])
        self.assertEqual(self.record["cross_section"]["width_um"], 0.343)
        self.assertEqual(self.record["cross_section"]["height_um"], 0.18)
        self.assertFalse(self.record["ready_pdk_migration"])

    def test_measurement_contract_covers_all_open_gates(self):
        evidence = set(self.record["required_external_evidence"])
        self.assertEqual(len(evidence), 5)
        self.assertTrue(self.record["test_vehicle"]["complex_s_parameter_required"])
        self.assertTrue(self.record["test_vehicle"]["pd_tia_must_be_measured_together"])
        self.assertEqual(self.record["test_vehicle"]["thermal_matrix_size"], [30, 30])

    def test_contract_is_fail_closed_and_blind_safe(self):
        self.assertFalse(self.record["p5_blind_rerun"])
        self.assertEqual(self.record["current_status"], "PRE_FABRICATION_OPEN")
        self.assertFalse(self.record["g4_physical_accepted"])
        self.assertFalse(self.record["g5_composition_complete"])
        self.assertFalse(self.record["p6_accepted"])


if __name__ == "__main__":
    unittest.main()
