import unittest

import numpy as np

from photonic_reservoir.benchmark import NarmaDivergenceError, delayed_input_features, evaluate_features, generate_mackey_glass, generate_narma, linear_memory_capacity, split_slices, supervised_alignment, validation_nmse
from photonic_reservoir.config import BenchmarkConfig


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.config = BenchmarkConfig(order=3, n_washout=10, n_train=40, n_validation=20, n_test=29, seeds=(11,))

    def test_split_is_disjoint_and_fits_supervised_length(self):
        slices = split_slices(self.config)
        self.assertEqual(slices["train"].stop, slices["validation"].start)
        self.assertEqual(slices["validation"].stop, slices["test"].start)
        self.assertEqual(slices["test"].stop, self.config.n_total - 1)

    def test_narma10_uses_expected_input_alignment(self):
        u, y = generate_narma(40, 10, 11)
        t = 10
        expected = 0.3 * y[t] + 0.05 * y[t] * np.sum(y[t - 9 : t + 1]) + 1.5 * u[t - 9] * u[t] + 0.1
        self.assertAlmostEqual(y[t + 1], expected)

    def test_divergent_narma_dataset_fails_instead_of_being_clipped(self):
        with self.assertRaisesRegex(NarmaDivergenceError, "seed 83"):
            generate_narma(12001, 10, 83)

    def test_replacement_publication_seed_is_finite(self):
        _, target = generate_narma(12001, 10, 113)
        self.assertTrue(np.all(np.isfinite(target)))

    def test_target_is_shifted_one_step(self):
        features = np.arange(self.config.n_total)[:, None]
        target = np.arange(self.config.n_total) * 2
        x, y = supervised_alignment(features, target)
        self.assertEqual(x[0, 0], 0)
        self.assertEqual(y[0], 2)

    def test_ridge_uses_correct_test_count(self):
        u, target = generate_narma(self.config.n_total, 3, 11)
        result = evaluate_features(delayed_input_features(u, 3), target, self.config)
        self.assertEqual(len(result.prediction), self.config.n_test)
        self.assertTrue(np.isfinite(result.test_nmse))

    def test_validation_score_does_not_require_test_values(self):
        u, target = generate_narma(self.config.n_total, 3, 11)
        features = delayed_input_features(u, 3)
        score, alpha = validation_nmse(features, target, self.config)
        self.assertTrue(np.isfinite(score))
        self.assertTrue(np.isfinite(alpha))

    def test_nonfinite_target_is_rejected(self):
        u, target = generate_narma(self.config.n_total, 3, 11)
        target[-1] = np.inf
        metric = evaluate_features(delayed_input_features(u, 3), target, self.config)
        self.assertEqual(metric.test_nmse, float("inf"))

    def test_memory_capacity_and_mackey_glass_are_finite(self):
        u, _ = generate_narma(self.config.n_total, 3, 11)
        memory = linear_memory_capacity(delayed_input_features(u, 3), u, self.config, max_delay=3)
        self.assertEqual(len(memory["capacity_per_delay"]), 3)
        self.assertTrue(np.isfinite(memory["total_capacity"]))
        self.assertTrue(np.all(np.isfinite(generate_mackey_glass(100, 11))))


if __name__ == "__main__":
    unittest.main()
