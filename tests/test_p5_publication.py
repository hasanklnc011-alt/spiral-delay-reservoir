import unittest

import numpy as np

from photonic_reservoir.p5_publication.preflight import _summarize, no_photonic_core_features


class P5PublicationTests(unittest.TestCase):
    def test_no_core_features_are_memoryless_and_finite(self):
        u = np.linspace(0.0, 0.5, 20)
        features = no_photonic_core_features(u)
        self.assertEqual(features.shape, (20, 3))
        self.assertTrue(np.all(np.isfinite(features)))

    def test_control_failure_blocks_candidate_lock(self):
        scores = {
            "photonic_candidate": {seed: 0.03 for seed in range(10)},
            "delayed_input": {seed: 0.10 for seed in range(10)},
            "same_delay_digital": {seed: 0.02 for seed in range(10)},
            "no_photonic_core": {seed: 0.20 for seed in range(10)},
        }
        config = {"required_controls": ["delayed_input", "same_delay_digital", "no_photonic_core"], "bootstrap_seed": 1, "bootstrap_samples": 1000, "relative_gain_threshold": 0.1, "median_gate": 0.04, "robust_seed_threshold": 0.05, "robust_seed_count": 8}
        summary = _summarize(scores, config)
        self.assertFalse(summary["controls"]["same_delay_digital"]["passed"])
        self.assertFalse(summary["all_publication_preconditions_passed"])


if __name__ == "__main__":
    unittest.main()
