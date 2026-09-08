"""Run the immutable P3 development-only physical tolerance screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from photonic_reservoir.p3_realistic.screen import load_json, run_screen
from photonic_reservoir.protocol import verify_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path("configs/p0_narma10_protocol.json"))
    parser.add_argument("--p2-result", type=Path, default=Path("p2-architecture/runs/screen-v4-pareto.json"))
    parser.add_argument("--config", type=Path, default=Path("p3-realistic/configs/screen-v1.json"))
    parser.add_argument("--output", type=Path, default=Path("p3-realistic/runs/screen-v1.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite immutable P3 result: {args.output}")
    protocol = load_json(args.protocol)
    verify_protocol(protocol)
    result = run_screen(protocol, load_json(args.p2_result), load_json(args.config))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"p3_gate_passed": result["p3_gate_passed"], "selected_candidate": result["selected_candidate"], "test_evaluations": 0, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
