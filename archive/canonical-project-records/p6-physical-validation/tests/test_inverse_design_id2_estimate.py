import ast
import unittest
from pathlib import Path

import inverse_design_id2_estimate as est


class InverseDesignID2EstimateTests(unittest.TestCase):
    def test_approval_is_required(self):
        with self.assertRaises(PermissionError):
            est.estimate(approved=False)

    def test_estimate_source_cannot_start_solve(self):
        tree = ast.parse(Path(est.__file__).read_text(encoding="utf-8"))
        attrs = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertNotIn("run", attrs)
        self.assertNotIn("start", attrs)
        self.assertIn("upload", attrs)
        self.assertIn("estimate_cost", attrs)


if __name__ == "__main__":
    unittest.main()
