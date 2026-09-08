import ast
import hashlib
import json
import unittest
from pathlib import Path

import autograd.numpy as anp

from inverse_design_simulation_preflight import phase_invariant_column_objective


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "inverse_design_simulation_preflight.py"
RESULT = HERE / "runs" / "inverse-design-simulation-preflight-v1.json"


class InverseDesignSimulationTests(unittest.TestCase):
    def test_source_has_no_cloud_calls(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        attrs = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertFalse({"upload", "run", "estimate_cost"} & attrs)

    def test_complex_objective_rewards_ideal_columns(self):
        ones = anp.ones(3)
        zeros = anp.zeros(3)
        splitter = phase_invariant_column_objective(
            ones / anp.sqrt(2), ones / anp.sqrt(2), zeros, 0.0
        )
        quadrature = phase_invariant_column_objective(
            ones / anp.sqrt(2), 1j * ones / anp.sqrt(2), zeros, 90.0
        )
        wrong_phase = phase_invariant_column_objective(
            ones / anp.sqrt(2), ones / anp.sqrt(2), zeros, 90.0
        )
        self.assertAlmostEqual(float(splitter), 1.0, places=12)
        self.assertAlmostEqual(float(quadrature), 1.0, places=12)
        self.assertLess(float(wrong_phase), float(quadrature))

    def test_saved_preflight_is_hash_locked_and_two_source(self):
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            result["source_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        )
        self.assertTrue(result["preflight_passed"])
        self.assertFalse(result["cloud_called"])
        self.assertEqual(result["combiner"]["source_count"], 2)
        self.assertFalse(result["id0_can_accept_device"])


if __name__ == "__main__":
    unittest.main()
