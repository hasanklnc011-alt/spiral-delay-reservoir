import unittest

from photonic_reservoir.p4_optimization.optimize import _summary


class P4OptimizationTests(unittest.TestCase):
    def test_summary_separates_data_and_hardware_seeds(self):
        rows = []
        for hardware_seed in (1, 2):
            for data_seed, score in ((11, 0.03), (23, 0.08), (37, 0.04)):
                rows.append({"hardware_seed": hardware_seed, "data_seed": data_seed, "validation_nmse": score})
        summary = _summary(rows, (11, 23, 37), 0.04, 2)
        self.assertEqual(summary["data_seeds_at_or_below_0_05"], 2)
        self.assertAlmostEqual(summary["median_validation_nmse"], 0.04)
        self.assertFalse(summary["passed"])

    def test_summary_passes_robust_fraction_gate(self):
        rows = [{"hardware_seed": index, "data_seed": index, "validation_nmse": 0.03} for index in range(10)]
        summary = _summary(rows, tuple(range(10)), 0.04, 8)
        self.assertTrue(summary["passed"])


if __name__ == "__main__":
    unittest.main()
