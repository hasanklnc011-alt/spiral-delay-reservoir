"""Create the immutable P5 candidate lock after a passing preflight."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from photonic_reservoir.protocol import canonical_sha256, source_tree_sha256, verify_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path("configs/p0_narma10_protocol_v2.json"))
    parser.add_argument("--candidate", type=Path, default=Path("p5-publication/configs/candidate-v2.json"))
    parser.add_argument("--preflight", type=Path, default=Path("p5-publication/runs/preflight-v2.json"))
    parser.add_argument("--output", type=Path, default=Path("p5-publication/candidate-lock-v2.json"))
    parser.add_argument("--blind-output", default="p5-publication/runs/blind-v2.json")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite candidate lock: {args.output}")
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    verify_protocol(protocol)
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    preflight = json.loads(args.preflight.read_text(encoding="utf-8"))
    if not preflight.get("candidate_lock_allowed"):
        raise PermissionError("candidate lock denied: development preflight did not pass")
    if preflight["p0_protocol_sha256"] != protocol["protocol_sha256"]:
        raise PermissionError("preflight references another protocol")
    if preflight["config_sha256"] != canonical_sha256(candidate):
        raise PermissionError("preflight references another candidate config")
    if preflight["source_sha256"] != source_tree_sha256():
        raise PermissionError("source changed after preflight")
    lock = {
        "status": "candidate_locked", "protocol_sha256": protocol["protocol_sha256"],
        "candidate_config_sha256": canonical_sha256(candidate), "source_sha256": source_tree_sha256(),
        "preflight_sha256": hashlib.sha256(args.preflight.read_bytes()).hexdigest(),
        "authorized_blind_output": args.blind_output,
        "locked_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.output.write_text(json.dumps(lock, indent=2), encoding="utf-8")
    print(json.dumps(lock, indent=2))


if __name__ == "__main__":
    main()
