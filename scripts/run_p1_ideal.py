"""Run the frozen P1 development-only ideal hypothesis benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from photonic_reservoir.p1_coherent_delay.ideal import load_json, run_development
from photonic_reservoir.protocol import verify_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=Path("configs/p0_narma10_protocol.json"))
    parser.add_argument("--config", type=Path, default=Path("p1-coherent-delay/configs/ideal-v1.json"))
    parser.add_argument("--output", type=Path, default=Path("p1-coherent-delay/runs/ideal-v1.json"))
    args = parser.parse_args()
    protocol = load_json(args.protocol)
    verify_protocol(protocol)
    config = load_json(args.config)
    result = run_development(protocol, config)
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite immutable P1 result: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({
        "median_validation_nmse": result["median_validation_nmse"],
        "p1_gate_passed": result["p1_gate_passed"],
        "test_evaluations": result["test_evaluations"],
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
