import ast
import json
import unittest
from pathlib import Path

import inverse_design_id2_preflight as pre


class InverseDesignID2PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = pre.preflight()

    def test_preflight_is_local_and_non_accepting(self):
        self.assertTrue(self.result["preflight_passed"])
        self.assertFalse(self.result["cloud_called"])
        self.assertFalse(self.result["id2_can_accept_device"])
        self.assertFalse(self.result["p5_blind_rerun"])

    def test_binary_seed_shapes_and_source_counts(self):
        self.assertEqual(self.result["devices"]["splitter"]["parameter_shape"], [150, 100, 1])
        self.assertEqual(self.result["devices"]["combiner"]["parameter_shape"], [200, 125, 1])
        self.assertEqual(self.result["devices"]["splitter"]["simulation_count"], 1)
        self.assertEqual(self.result["devices"]["combiner"]["simulation_count"], 2)
        self.assertNotEqual(
            self.result["devices"]["splitter"]["binary_seed_sha256"],
            self.result["devices"]["combiner"]["binary_seed_sha256"],
        )

    def test_source_has_no_cloud_calls(self):
        tree = ast.parse(Path(pre.__file__).read_text(encoding="utf-8"))
        forbidden = {"run", "start", "upload", "estimate_cost"}
        attrs = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(forbidden.isdisjoint(attrs))


if __name__ == "__main__":
    unittest.main()
