import inspect
import unittest

import g3d_mmi_eme_screen as screen


class G3DEMEPolicyTests(unittest.TestCase):
    def test_preflight_is_no_cloud_and_length_only(self):
        record = screen.preflight()
        self.assertTrue(record["preflight_passed"])
        self.assertFalse(record["cloud_called"])
        self.assertFalse(record["p5_blind_rerun"])
        self.assertEqual(record["eme_cells"], 19)
        self.assertEqual(record["length_sweep_points"], 49)
        self.assertEqual(record["mmi_cell_index"], 9)

    def test_paid_paths_are_approval_and_task_lock_guarded(self):
        source = inspect.getsource(screen)
        self.assertIn("User credit approval required", source)
        self.assertIn("User solve approval required", source)
        self.assertIn('task_id_cached=locked["task_id"]', source)
        self.assertIn("Source changed after estimate", source)
        self.assertIn("Locked simulation mismatch", source)

    def test_screen_cannot_directly_accept_g3d(self):
        source = inspect.getsource(screen.analyze)
        self.assertIn("no G3-D acceptance", source)
        self.assertIn("full_s_max_singular_value", source)


if __name__ == "__main__":
    unittest.main()
