import unittest

import numpy as np

from photonic_reservoir.p3_realistic.screen import architecture_feasibility, physical_sparse_features


PHYSICAL = {
    "symbol_rate_hz": 10e9, "group_index": 4.0, "max_delay_length_cm": 20.0,
    "detector_bandwidth_hz": 50e9, "max_switch_rate_hz": 100e9,
    "waveguide_loss_db_per_cm": 0.2, "switch_insertion_loss_db": 1.0,
    "combiner_insertion_loss_db": 0.5, "extinction_ratio_db": 30.0,
    "signal_power_mw": 1.0, "lo_power_mw": 1.0,
    "static_phase_error_deg": 1.0, "dynamic_phase_jitter_deg": 0.5,
    "lo_amplitude_drift_fraction": 0.001, "responsivity_a_per_w": 0.8,
    "thermal_noise_a_per_sqrt_hz": 1e-11,
}


class P3RealisticTests(unittest.TestCase):
    def test_single_detector_fails_real_time_bandwidth_gate(self):
        result = architecture_feasibility(30, 1, 20, PHYSICAL)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["detector_bandwidth"])

    def test_five_ports_pass_nominal_architecture_gate(self):
        result = architecture_feasibility(30, 5, 20, PHYSICAL)
        self.assertTrue(result["passed"])
        self.assertEqual(result["time_multiplex_steps"], 6)

    def test_physical_features_are_finite_and_deterministic(self):
        delayed = np.arange(120, dtype=float).reshape(24, 5) / 240.0
        labels = ["self:0", "lo:1", "pair:2,4"]
        first = physical_sparse_features(delayed, labels, PHYSICAL, 3, 91)
        second = physical_sparse_features(delayed, labels, PHYSICAL, 3, 91)
        np.testing.assert_array_equal(first, second)
        self.assertTrue(np.all(np.isfinite(first)))

    def test_invalid_label_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid primitive"):
            physical_sparse_features(np.zeros((10, 5)), ["bad:1"], PHYSICAL, 1, 1)

    def test_more_parallel_ports_reduce_receiver_noise_bandwidth(self):
        delayed = np.tile(np.linspace(0.0, 0.5, 5), (200, 1))
        labels = ["self:0", "lo:1", "pair:2,4"]
        noisy = dict(PHYSICAL, thermal_noise_a_per_sqrt_hz=1e-9)
        one_port = physical_sparse_features(delayed, labels, noisy, 1, 77)
        three_ports = physical_sparse_features(delayed, labels, noisy, 3, 77)
        self.assertGreater(float(np.std(one_port[:, 0])), float(np.std(three_ports[:, 0])))


if __name__ == "__main__":
    unittest.main()
