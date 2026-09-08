import unittest
from dataclasses import replace

import numpy as np

from photonic_reservoir.config import DriveConfig, FeedbackParams, RingParams, SolverConfig, TopologyParams, physical_validity
from photonic_reservoir.model import encoded_power, linear_s21, simulate


class ModelTests(unittest.TestCase):
    def test_ring_q_and_lifetime_are_consistent(self):
        ring = RingParams()
        self.assertAlmostEqual(1.0 / ring.q_loaded, 1.0 / ring.q_int + 1.0 / ring.q_ext)
        self.assertAlmostEqual(ring.tau_field_s, 2.0 * ring.q_loaded / ring.omega0)

    def test_input_power_is_nonnegative(self):
        drive = DriveConfig()
        self.assertGreaterEqual(encoded_power(0.0, 1.0, drive), drive.minimum_power_w)

    def test_linear_s21_is_finite(self):
        topology = TopologyParams(kerr_enabled=False)
        response = linear_s21(topology, np.linspace(-2e12, 2e12, 101))
        self.assertTrue(np.all(np.isfinite(response)))

    def test_simulation_shapes_and_determinism(self):
        topology = TopologyParams(kerr_enabled=False)
        drive = DriveConfig(n_virtual=4, symbol_time_s=1e-12)
        u = np.linspace(0.0, 0.5, 12)
        first = simulate(u, topology, drive)
        second = simulate(u, topology, drive)
        self.assertEqual(first.features.shape, (12, 4))
        self.assertEqual(first.cavity_energy_j.shape, (12, 4, 3))
        np.testing.assert_allclose(first.features, second.features)

    def test_memory_reset_changes_trajectory(self):
        topology = TopologyParams(kerr_enabled=False)
        u = np.array([0.1, 0.4, 0.2, 0.3])
        persistent = simulate(u, topology, DriveConfig(n_virtual=3))
        reset = simulate(u, topology, DriveConfig(n_virtual=3, reset_each_symbol=True))
        self.assertFalse(np.allclose(persistent.features, reset.features, rtol=1e-10, atol=1e-14))

    def test_delay_feedback_runs(self):
        topology = TopologyParams(kerr_enabled=False)
        result = simulate(np.full(8, 0.2), topology, DriveConfig(n_virtual=3), feedback=FeedbackParams(True, 0.2, 0.0, 1e-12))
        self.assertFalse(result.diverged)

    def test_cavity_and_delay_memory_reset_independently(self):
        topology = TopologyParams(kerr_enabled=False)
        u = np.array([0.1, 0.4, 0.2, 0.3, 0.15, 0.35])
        drive = DriveConfig(n_virtual=3)
        feedback = FeedbackParams(True, 0.5, 0.0, 1e-12)
        persistent = simulate(u, topology, drive, feedback=feedback)
        cavity_only = simulate(u, topology, replace(drive, reset_each_symbol=True), feedback=feedback)
        delay_only = simulate(u, topology, drive, feedback=replace(feedback, reset_each_symbol=True))
        both = simulate(u, topology, replace(drive, reset_each_symbol=True), feedback=replace(feedback, reset_each_symbol=True))
        # Resetting the ring state must not silently carry the delay line along.
        for other in (cavity_only, delay_only, both):
            self.assertFalse(np.allclose(persistent.features, other.features, rtol=1e-10, atol=1e-14))
        self.assertFalse(np.allclose(cavity_only.features, delay_only.features, rtol=1e-10, atol=1e-14))
        self.assertFalse(np.allclose(cavity_only.features, both.features, rtol=1e-10, atol=1e-14))

    def test_delay_reset_matches_feedback_off_within_one_symbol_delay(self):
        # Clearing history every symbol with a one-symbol delay leaves nothing to
        # interpolate, so the run must collapse onto the no-feedback trajectory.
        topology = TopologyParams(kerr_enabled=False)
        u = np.array([0.1, 0.4, 0.2, 0.3])
        drive = DriveConfig(n_virtual=3, symbol_time_s=1e-12)
        reset_delay = simulate(u, topology, drive, feedback=FeedbackParams(True, 0.6, 0.0, 1e-12, reset_each_symbol=True))
        no_feedback = simulate(u, topology, drive)
        np.testing.assert_allclose(reset_delay.features, no_feedback.features, rtol=1e-9, atol=1e-15)

    def test_fsr_is_consistent_with_round_trip_time(self):
        ring = RingParams()
        round_trip_s = ring.group_index * ring.circumference_m / 299_792_458.0
        self.assertAlmostEqual(ring.fsr_hz * round_trip_s, 1.0, places=12)

    def test_physical_validity_tracks_the_calibrated_band(self):
        topology = TopologyParams(kerr_enabled=False)
        # 20 nodes across 0.2 ps is a 100 THz node rate: far outside the 2.4 THz
        # window the FDTD spectrum actually covers.
        fast = physical_validity(topology, DriveConfig(n_virtual=20, symbol_time_s=0.2e-12))
        self.assertFalse(fast["within_calibrated_band"])
        self.assertGreater(fast["node_rate_over_band"], 40.0)
        slow = physical_validity(topology, DriveConfig(n_virtual=20, symbol_time_s=20e-12))
        self.assertTrue(slow["within_calibrated_band"])

    def test_single_ring_reaches_analytic_steady_state(self):
        ring = RingParams(detuning_linewidths=0.0)
        topology = TopologyParams(rings=(ring,), coupling_linewidths=(), coupling_phases_rad=(), kerr_enabled=False)
        drive = DriveConfig(n_virtual=1, symbol_time_s=1e-12, power_bias_w=0.05, power_modulation_w=0.0)
        result = simulate(np.full(100, 0.25), topology, drive)
        expected = linear_s21(topology, np.array([0.0]))[0] * np.sqrt(0.05)
        self.assertAlmostEqual(result.through_field[-1, -1].real, expected.real, places=6)
        self.assertAlmostEqual(result.through_field[-1, -1].imag, expected.imag, places=6)

    def test_time_step_refinement_changes_features_below_one_percent(self):
        topology = TopologyParams(kerr_enabled=False)
        drive = DriveConfig(n_virtual=4)
        u = np.linspace(0.0, 0.5, 20)
        coarse = simulate(u, topology, drive, SolverConfig(steps_per_min_lifetime=12.0))
        fine = simulate(u, topology, drive, SolverConfig(steps_per_min_lifetime=24.0))
        relative = np.linalg.norm(coarse.features - fine.features) / np.linalg.norm(fine.features)
        self.assertLess(relative, 0.01)


if __name__ == "__main__":
    unittest.main()
