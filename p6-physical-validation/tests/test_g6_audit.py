import unittest
from g6_acceptance_audit import audit
class G6AuditTests(unittest.TestCase):
    def test_audit_is_fail_closed_and_blind_safe(self):
        result=audit();self.assertFalse(result["p5_blind_rerun"]);self.assertFalse(result["p6_accepted"]);self.assertEqual(result["verdict"],"NOT_PHYSICALLY_ACCEPTED")
    def test_pass_fail_open_requirements_are_explicit(self):
        r=audit()["requirements"];self.assertEqual(r["G1_delay_cross_section"]["status"],"PASS");self.assertEqual(r["G2_layout"]["status"],"PASS");self.assertEqual(r["G3C_splitter_tap"]["status"],"FAIL_REDESIGN");self.assertEqual(r["G3D_coherent_combiner"]["status"],"FAIL_REDESIGN")
if __name__=="__main__":unittest.main()
