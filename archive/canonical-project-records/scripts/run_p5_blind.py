"""Run the single authorized P5 blind evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from photonic_reservoir.p5_publication.blind import load_json, run_blind
from photonic_reservoir.protocol import verify_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path("configs/p0_narma10_protocol_v2.json"))
    parser.add_argument("--p2-result", type=Path, default=Path("p2-architecture/runs/screen-v4-pareto.json"))
    parser.add_argument("--p3-config", type=Path, default=Path("p3-realistic/configs/screen-v1.json"))
    parser.add_argument("--candidate", type=Path, default=Path("p5-publication/configs/candidate-v2.json"))
    parser.add_argument("--lock", type=Path, default=Path("p5-publication/candidate-lock-v2.json"))
    parser.add_argument("--output", type=Path, default=Path("p5-publication/runs/blind-v2.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"blind evaluation already consumed: {args.output}")
    protocol = load_json(args.protocol)
    verify_protocol(protocol)
    lock = load_json(args.lock)
    if str(args.output).replace("\\", "/") != str(lock.get("authorized_blind_output", "")).replace("\\", "/"):
        raise PermissionError("requested blind output is not the locked authorized path")
    result = run_blind(protocol, load_json(args.p2_result), load_json(args.p3_config), load_json(args.candidate), lock, args.lock)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"summary": result["summary"], "blind_datasets_evaluated": result["blind_datasets_evaluated"], "test_evaluations": result["test_evaluations"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
