import unittest

import numpy as np

from photonic_reservoir.benchmark import delayed_input_features, generate_narma, validation_nmse
from photonic_reservoir.config import BenchmarkConfig
from photonic_reservoir.p1_coherent_delay.ideal import coherent_square_law_features, delayed_fields, fast_validation_nmse, full_quadratic_features


class P1IdealTests(unittest.TestCase):
    def test_quadratic_and_coherent_feature_counts(self):
        delayed = np.arange(100, dtype=float).reshape(20, 5) / 100.0
        self.assertEqual(full_quadratic_features(delayed).shape[1], 20)
        self.assertEqual(coherent_square_law_features(delayed).shape[1], 20)
        self.assertEqual(coherent_square_law_features(delayed, include_local_oscillator=False).shape[1], 15)

    def test_coherent_field_u_spans_full_quadratic_oracle(self):
        rng = np.random.default_rng(20260903)
        delayed = rng.uniform(0.0, 0.5, size=(500, 6))
        oracle = full_quadratic_features(delayed)
        coherent = coherent_square_law_features(delayed)
        design = np.column_stack((np.ones(len(coherent)), coherent))
        weights, *_ = np.linalg.lstsq(design, oracle, rcond=None)
        residual = np.linalg.norm(design @ weights - oracle) / np.linalg.norm(oracle)
        self.assertLess(residual, 1e-10)

    def test_sqrt_power_encoding_is_finite_and_distinct(self):
        u = np.linspace(0.0, 0.5, 100)
        field_u = delayed_fields(u, 5, "field_u")
        sqrt_power = delayed_fields(u, 5, "sqrt_power", power_bias=1.0, power_scale=1.0)
        self.assertTrue(np.all(np.isfinite(sqrt_power)))
        self.assertFalse(np.allclose(field_u, sqrt_power))

    def test_fast_validation_matches_reference_ridge(self):
        config = BenchmarkConfig(order=3, n_washout=20, n_train=200, n_validation=100, n_test=0, seeds=(11,), ridge_alphas=(1e-6, 1e-3, 1.0))
        u, target = generate_narma(config.n_total, 3, 11)
        features = full_quadratic_features(delayed_input_features(u, 4))
        reference_score, reference_alpha = validation_nmse(features, target, config)
        result = fast_validation_nmse(features, target, config)
        self.assertAlmostEqual(result.validation_nmse, reference_score, places=10)
        self.assertEqual(result.best_alpha, reference_alpha)

    def test_p1_rejects_any_test_slice(self):
        config = BenchmarkConfig(order=3, n_washout=10, n_train=40, n_validation=20, n_test=10, seeds=(11,))
        u, target = generate_narma(config.n_total, 3, 11)
        with self.assertRaisesRegex(ValueError, "n_test=0"):
            fast_validation_nmse(u[:, None], target, config)


if __name__ == "__main__":
    unittest.main()
