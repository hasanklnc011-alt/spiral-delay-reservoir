import ast
import json
import unittest
from pathlib import Path

import autograd.numpy as anp

import inverse_design_id1_run as run


class InverseDesignID1RunTests(unittest.TestCase):
    def test_gate_requires_approval_and_honors_allocations(self):
        with self.assertRaises(PermissionError):
            run.validate_gate("splitter", approved=False)
        for device in run.DEVICE_PLAN:
            gate = run.validate_gate(device, approved=True)
            self.assertLessEqual(gate["estimated_cost_fc"], gate["allocation_fc"])
            self.assertEqual(run.DEVICE_PLAN[device]["cache"].suffix, ".hdf5")

    def test_estimate_is_fail_closed(self):
        estimate = json.loads(run.ESTIMATE_RECORD.read_text(encoding="utf-8"))
        self.assertTrue(estimate["within_total_limit"])
        self.assertTrue(estimate["optimization_allowed"])
        self.assertFalse(estimate["solve_started"])

    def test_combiner_reflections_are_summed_per_frequency(self):
        unit = anp.ones(3) / anp.sqrt(2.0)
        zero = anp.zeros(3)
        score = run._combiner_column_objective(unit, 1j * unit, (zero, zero), 90.0)
        self.assertAlmostEqual(float(score), 1.0, places=12)

    def test_cloud_execution_is_only_in_explicit_execute_path(self):
        tree = ast.parse(Path(run.__file__).read_text(encoding="utf-8"))
        execute_fn = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "execute"
        )
        calls = [
            node for node in ast.walk(execute_fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
        ]
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
