import json
import unittest
from pathlib import Path

from g3_straight_preflight import HERE
from g3d_mmi_fdtd import sha256


class InverseDesignID2ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = HERE / "runs" / "inverse-design-id2-binary-fdtd-v1.json"
        cls.result = json.loads(cls.path.read_text(encoding="utf-8"))

    def test_result_is_fail_closed_and_blind_free(self):
        self.assertFalse(self.result["p5_blind_rerun"])
        self.assertFalse(self.result["id2_all_metric_pass"])
        self.assertFalse(self.result["devices_accepted"])
        self.assertEqual(self.result["disposition"], "FAIL_REDESIGN")

    def test_both_devices_failed_metrics(self):
        self.assertFalse(self.result["devices"]["splitter"]["metrics"]["id2_metric_pass"])
        self.assertFalse(self.result["devices"]["combiner"]["metrics"]["id2_metric_pass"])

    def test_data_files_exist(self):
        paths = [self.result["devices"]["splitter"]["data_file"]]
        paths.extend(self.result["devices"]["combiner"]["data_files"])
        for relative in paths:
            self.assertTrue((HERE / relative).is_file())

    def test_source_and_estimate_are_hash_locked(self):
        self.assertEqual(self.result["source_sha256"], sha256(HERE / "inverse_design_id2_run.py"))
        self.assertEqual(
            self.result["estimate_record_sha256"],
            sha256(HERE / "runs" / "inverse-design-id2-estimate-v1.json"),
        )


if __name__ == "__main__":
    unittest.main()
