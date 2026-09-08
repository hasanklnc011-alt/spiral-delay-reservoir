import unittest

import numpy as np

from photonic_reservoir.p2_architecture.screen import channel_labels, normalized_binary_masks, random_mzi_intensities


class P2ArchitectureTests(unittest.TestCase):
    def test_channel_labels_match_p1_primitive_basis(self):
        labels = channel_labels(5)
        self.assertEqual(len(labels), 20)
        self.assertEqual(labels[:5], ["self:0", "self:1", "self:2", "self:3", "self:4"])
        self.assertEqual(labels[5], "lo:0")
        self.assertEqual(labels[-1], "pair:3,4")

    def test_binary_masks_are_deterministic_and_unit_norm(self):
        first = normalized_binary_masks(12, 5, 101)
        second = normalized_binary_masks(12, 5, 101)
        np.testing.assert_array_equal(first, second)
        np.testing.assert_allclose(np.linalg.norm(first, axis=1), 1.0)

    def test_random_mzi_channel_count_and_finiteness(self):
        fields = np.arange(50, dtype=float).reshape(10, 5) / 100.0
        masks = normalized_binary_masks(7, 5, 211)
        intensity = random_mzi_intensities(fields, masks)
        self.assertEqual(intensity.shape, (10, 7))
        self.assertTrue(np.all(np.isfinite(intensity)))

    def test_random_mzi_rejects_dimension_mismatch(self):
        with self.assertRaisesRegex(ValueError, "dimensions do not match"):
            random_mzi_intensities(np.zeros((10, 5)), np.zeros((7, 4)))

    def test_twenty_lags_have_230_primitive_channels(self):
        self.assertEqual(len(channel_labels(20)), 230)


if __name__ == "__main__":
    unittest.main()
