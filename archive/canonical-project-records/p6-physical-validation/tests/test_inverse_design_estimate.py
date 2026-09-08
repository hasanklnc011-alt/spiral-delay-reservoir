import ast
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "inverse_design_estimate.py"


class InverseDesignEstimateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.text)

    def test_estimate_requires_approval_and_preflight_hashes(self):
        self.assertIn("if not approved:", self.text)
        self.assertIn("Simulation source changed after preflight", self.text)
        self.assertIn("Inverse-design config changed after preflight", self.text)

    def test_estimate_source_cannot_start_a_solve(self):
        attrs = {
            node.attr for node in ast.walk(self.tree) if isinstance(node, ast.Attribute)
        }
        self.assertIn("upload", attrs)
        self.assertIn("estimate_cost", attrs)
        self.assertNotIn("run", attrs)
        self.assertNotIn("start", attrs)

    def test_forward_plus_adjoint_budget_is_explicit(self):
        self.assertIn("2.0 * splitter_forward", self.text)
        self.assertIn("2.0 * combiner_forward", self.text)
        self.assertIn("ID1_TOTAL_LIMIT_FC = 1.5", self.text)


if __name__ == "__main__":
    unittest.main()
