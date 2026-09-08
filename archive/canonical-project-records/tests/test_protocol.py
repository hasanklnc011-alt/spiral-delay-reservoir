import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from photonic_reservoir.protocol import guard_reserved_blind_seeds, load_and_verify_protocol, require_blind_authorization


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = PROJECT_ROOT / "configs" / "p0_narma10_protocol.json"
PROTOCOL_V2_PATH = PROJECT_ROOT / "configs" / "p0_narma10_protocol_v2.json"


class P0ProtocolTests(unittest.TestCase):
    def test_frozen_protocol_and_dataset_commitments_verify(self):
        _, report = load_and_verify_protocol(PROTOCOL_PATH)
        self.assertEqual(report["datasets_verified"], 20)

    def test_v2_protocol_and_new_blind_commitments_verify(self):
        protocol, report = load_and_verify_protocol(PROTOCOL_V2_PATH)
        self.assertEqual(report["datasets_verified"], 20)
        self.assertEqual(protocol["supersedes"]["v1_blind_test_evaluations"], 0)
        old_protocol, _ = load_and_verify_protocol(PROTOCOL_PATH)
        self.assertTrue(set(protocol["publication_blind"]["seeds"]).isdisjoint(old_protocol["publication_blind"]["seeds"]))

    def test_blind_suite_is_sealed_without_candidate_lock(self):
        protocol, _ = load_and_verify_protocol(PROTOCOL_PATH)
        with self.assertRaisesRegex(PermissionError, "candidate lock is missing"):
            require_blind_authorization(protocol, PROJECT_ROOT / "candidate-lock.json")

    def test_main_experiment_guard_rejects_any_reserved_seed(self):
        with self.assertRaisesRegex(PermissionError, "--candidate-lock is required"):
            guard_reserved_blind_seeds((11, 127))

    def test_main_experiment_guard_allows_development_seeds(self):
        guard_reserved_blind_seeds((11, 23, 113))

    def test_main_experiment_guard_compares_running_config_to_lock(self):
        protocol, _ = load_and_verify_protocol(PROTOCOL_PATH)
        with TemporaryDirectory() as directory:
            lock_path = Path(directory) / "candidate-lock.json"
            lock_path.write_text(
                json.dumps({
                    "status": "candidate_locked",
                    "protocol_sha256": protocol["protocol_sha256"],
                    "candidate_config_sha256": "0" * 64,
                    "source_sha256": "0" * 64,
                    "locked_utc": "2026-09-03T00:00:00Z",
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PermissionError, "running config does not match"):
                guard_reserved_blind_seeds((127,), lock_path, "1" * 64)

    def test_tampered_lock_is_rejected(self):
        protocol, _ = load_and_verify_protocol(PROTOCOL_PATH)
        with TemporaryDirectory() as directory:
            lock_path = Path(directory) / "candidate-lock.json"
            lock_path.write_text(json.dumps({"status": "candidate_locked"}), encoding="utf-8")
            with self.assertRaisesRegex(PermissionError, "another protocol"):
                require_blind_authorization(protocol, lock_path)


if __name__ == "__main__":
    unittest.main()
