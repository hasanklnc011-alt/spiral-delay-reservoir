import sys
import unittest
from pathlib import Path


P6_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P6_ROOT))

from component_model import (  # noqa: E402
    build_report,
    coherence_metrics,
    delay_metrics,
    ideal_combiner_output_power,
    load_config,
    routing_metrics,
    slot_power_metrics,
    validate_architecture,
    verify_provenance,
)


class P6ComponentModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()

    def test_p5_blind_policy_is_immutable(self):
        policy = self.config["blind_policy"]
        self.assertFalse(policy["rerun_allowed"])
        self.assertFalse(policy["tuning_from_blind_allowed"])
        provenance = verify_provenance(self.config)
        self.assertTrue(provenance["passed"])
        self.assertTrue(provenance["candidate_config_canonical_matches"])
        self.assertTrue(provenance["routing_labels_match_p4"])

    def test_locked_architecture_is_30_channels_10_pd_3_slots(self):
        validate_architecture(self.config)
        arch = self.config["architecture"]
        self.assertEqual(arch["channel_count"], 30)
        self.assertEqual(arch["parallel_pd_count"], 10)
        self.assertEqual(arch["time_multiplex_slots"], 3)

    def test_group_index_four_reproduces_locked_delay_length(self):
        result = delay_metrics(self.config)
        self.assertAlmostEqual(result["required_length_cm"], 14.240141755, places=9)
        self.assertAlmostEqual(result["symbols_at_locked_length"], 19.0, places=9)

    def test_legacy_sin_cross_section_fails_19_symbol_delay(self):
        legacy_ng = self.config["platform_gate"]["legacy_reference_only"]["group_index"]
        result = delay_metrics(self.config, group_index=legacy_ng)
        self.assertLess(result["symbols_at_locked_length"], 11.0)
        self.assertGreater(result["required_length_cm"], 27.0)

    def test_slot_power_is_below_p4_conservative_bound(self):
        slots = slot_power_metrics(self.config)
        bound = self.config["optical_power"]["p4_conservative_simultaneous_budget_mw"]
        self.assertEqual(len(slots), 3)
        self.assertLessEqual(max(slot["normalized_arm_power_mw_at_u_equal_1"] for slot in slots), bound)
        self.assertLess(max(slot["encoded_peak_arm_power_mw_at_u_max"] for slot in slots), bound)

    def test_report_cannot_claim_physical_acceptance_at_start(self):
        report = build_report(self.config, check_provenance=True)
        self.assertEqual(report["gates"]["p5_provenance"], "PASS")
        self.assertEqual(report["gates"]["group_index_mode_solve"], "OPEN")
        self.assertFalse(report["p6_accepted"])

    def test_thermal_trim_is_not_used_as_30ghz_switch(self):
        report = build_report(self.config)
        self.assertFalse(report["thermal"]["thermal_can_reconfigure_per_slot"])
        self.assertEqual(report["thermal"]["thermal_trim_role"], "static_only")

    def test_exact_pd_by_slot_routing_and_multicast_are_exposed(self):
        routing = routing_metrics(self.config)
        self.assertEqual(routing["pd_by_slot"][0], ["pair:0,9", "lo:10", "pair:8,17"])
        self.assertEqual(routing["pd_by_slot"][9], ["pair:4,13", "pair:7,16", "self:18"])
        self.assertEqual(routing["maximum_same_slot_tap_fanout"], 2)
        self.assertAlmostEqual(routing["maximum_intentional_multicast_division_db"], 3.0102999566, places=9)

    def test_maximum_coherent_differential_delay_is_1_4_ns(self):
        result = coherence_metrics(self.config)
        self.assertEqual(result["maximum_differential_delay_symbols"], 14.0)
        self.assertAlmostEqual(result["maximum_differential_delay_s"], 1.4e-9, places=18)
        self.assertGreater(result["laser_linewidth_hz_if_all_2deg_rms_budget"], 138e3)
        self.assertLess(result["laser_linewidth_hz_if_all_2deg_rms_budget"], 139e3)

    def test_ideal_combiner_is_power_conserving_across_both_outputs(self):
        for phase in (0.0, 0.7, 3.141592653589793):
            first = ideal_combiner_output_power(5.0, 5.0, phase)
            second = ideal_combiner_output_power(5.0, 5.0, phase + 3.141592653589793)
            self.assertAlmostEqual(first + second, 10.0, places=12)

    def test_receiver_keeps_p5_50ghz_and_exposes_saturation_gap(self):
        receiver = build_report(self.config)["receiver"]
        self.assertEqual(receiver["system_minimum_bandwidth_hz"], 15e9)
        self.assertEqual(receiver["p5_model_compatibility_bandwidth_hz"], 50e9)
        self.assertAlmostEqual(receiver["lo_only_current_before_combiner_a"], 0.004)
        self.assertAlmostEqual(receiver["lo_only_current_one_ideal_output_a"], 0.002)
        self.assertEqual(receiver["pd_saturation_status"], "OPEN")

    def test_progressive_tap_bus_has_20_equal_power_couplings(self):
        loss = build_report(self.config)["loss"]
        kappas = loss["lossless_progressive_tap_kappa_power"]
        self.assertEqual(len(kappas), 20)
        self.assertAlmostEqual(kappas[0], 1.0 / 20.0)
        self.assertEqual(kappas[-1], 1.0)
        self.assertEqual(loss["signal_progressive_tap_sections"], 19)


if __name__ == "__main__":
    unittest.main()
