"""Verify the frozen P0 dataset commitments; optionally check a candidate lock."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from photonic_reservoir.protocol import load_and_verify_protocol, require_blind_authorization


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path("configs/p0_narma10_protocol.json"))
    parser.add_argument("--candidate-lock", type=Path)
    args = parser.parse_args()
    protocol, report = load_and_verify_protocol(args.protocol)
    report["blind_test_authorized"] = False
    if args.candidate_lock is not None:
        require_blind_authorization(protocol, args.candidate_lock)
        report["blind_test_authorized"] = True
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
