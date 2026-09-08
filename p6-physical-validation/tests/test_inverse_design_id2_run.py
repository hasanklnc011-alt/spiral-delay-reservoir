import ast
import unittest
from pathlib import Path

import inverse_design_id2_run as run


class InverseDesignID2RunTests(unittest.TestCase):
    def test_gate_requires_approval_and_is_under_limit(self):
        with self.assertRaises(PermissionError):
            run.validate_gate(False)
        estimate = run.validate_gate(True)
        self.assertLess(estimate["estimated_total_flexcredits"], estimate["id2_limit_flexcredits"])

    def test_cloud_run_is_only_in_execute(self):
        tree = ast.parse(Path(run.__file__).read_text(encoding="utf-8"))
        execute_fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "execute")
        calls = [
            node for node in ast.walk(execute_fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
        ]
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
