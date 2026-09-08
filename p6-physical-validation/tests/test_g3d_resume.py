import inspect
import unittest

import g3d_mmi_resume_v1 as resume


class G3DResumeTests(unittest.TestCase):
    def test_resume_uses_only_cached_locked_tasks(self):
        source = inspect.getsource(resume)
        self.assertIn('task_id_cached=item["task_id"]', source)
        self.assertIn("Locked builder changed after estimate", source)
        self.assertIn("Locked simulation mismatch", source)
        self.assertIn('"solve_restarted": False', source)

    def test_string_log_decay_parser(self):
        class Data:
            log = "field decay: 1.0e-3\nfield decay: 5.9e-08"

        self.assertEqual(resume.final_decay(Data()), 5.9e-8)

    def test_saved_result_is_compact_but_spectral_evidence_is_hashed(self):
        source = inspect.getsource(resume.resume)
        self.assertIn('if key != "per_wavelength"', source)
        self.assertIn('measured["per_wavelength_sha256"]', source)
        self.assertIn('measured["per_wavelength_points"]', source)


if __name__ == "__main__":
    unittest.main()
