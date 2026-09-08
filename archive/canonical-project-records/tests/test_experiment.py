import unittest

from photonic_reservoir.config import BenchmarkConfig
from photonic_reservoir.experiment import summarize_gates


class ExperimentGateTests(unittest.TestCase):
    def _rows(self):
        rows = []
        for seed in (1, 2, 3):
            rows.extend([
                {"seed": seed, "variant": "delayed_input", "test_nmse": 0.40},
                {"seed": seed, "variant": "three_ring_physical_kerr", "test_nmse": 0.20},
                {"seed": seed, "variant": "three_ring_kerr_off", "test_nmse": 0.25},
            ])
        return rows

    def test_narma3_never_opens_cloud_gate(self):
        summary = summarize_gates(self._rows(), BenchmarkConfig(order=3, n_train=6000, n_validation=2000, n_test=3000, seeds=tuple(range(10))))
        self.assertTrue(summary["system_vs_delayed_input"]["passed"])
        self.assertFalse(summary["fdtd_cloud_gate_open"])

    def test_narma10_can_open_cloud_gate(self):
        publication_rows = []
        for seed in range(10):
            publication_rows.extend([
                {"seed": seed, "variant": "delayed_input", "test_nmse": 0.40},
                {"seed": seed, "variant": "three_ring_physical_kerr", "test_nmse": 0.20},
                {"seed": seed, "variant": "three_ring_kerr_off", "test_nmse": 0.25},
            ])
        summary = summarize_gates(publication_rows, BenchmarkConfig(order=10, n_train=6000, n_validation=2000, n_test=3000, seeds=tuple(range(10))))
        self.assertTrue(summary["fdtd_cloud_gate_open"])

    def test_short_narma10_screen_never_opens_cloud_gate(self):
        summary = summarize_gates(self._rows(), BenchmarkConfig(order=10, n_train=400, n_validation=150, n_test=249, seeds=(1, 2, 3)))
        self.assertFalse(summary["fdtd_cloud_gate_open"])


if __name__ == "__main__":
    unittest.main()
