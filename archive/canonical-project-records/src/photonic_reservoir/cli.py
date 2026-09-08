"""LEGACY command-line entry points retained for three-ring reproducibility."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from .config import BenchmarkConfig, DriveConfig, FeedbackParams, SolverConfig, TopologyParams, benchmark_from_dict, topology_from_dict
from .evidence import write_inventory
from .delay_search import bounded_delay_search, write_delay_search
from .experiment import run_ablation, write_run
from .fdtd_validation import write_validation
from .search import bounded_search, write_search


def load_config(path: Path) -> tuple[TopologyParams, DriveConfig, SolverConfig, BenchmarkConfig, FeedbackParams]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return (
        topology_from_dict(data["topology"]),
        DriveConfig(**data["drive"]),
        SolverConfig(**data.get("solver", {})),
        benchmark_from_dict(data["benchmark"]),
        FeedbackParams(**data.get("feedback", {})),
    )


def _run(args: argparse.Namespace) -> None:
    project_dir = Path(args.project_dir).resolve()
    config_path = Path(args.config).resolve()
    topology, drive, solver, benchmark, feedback = load_config(config_path)
    lock_path = Path(args.candidate_lock).resolve() if args.candidate_lock else None
    config_sha256 = hashlib.sha256(config_path.read_bytes()).hexdigest()
    payload = run_ablation(topology, drive, solver, benchmark, feedback, lock_path, config_sha256)
    configs = {
        "topology": asdict(topology),
        "drive": asdict(drive),
        "solver": asdict(solver),
        "benchmark": asdict(benchmark),
        "feedback": asdict(feedback),
    }
    run_dir = write_run(project_dir / "legacy-three-ring" / "runs", payload, configs, project_dir.parents[1])
    print(json.dumps(payload["summary"], indent=2))
    print(f"run_id={run_dir.name}")


def _evidence(args: argparse.Namespace) -> None:
    write_inventory(Path(args.source).resolve(), Path(args.output).resolve())
    print(f"evidence_manifest={Path(args.output).name}")


def _search(args: argparse.Namespace) -> None:
    topology, drive, solver, benchmark, _ = load_config(Path(args.config).resolve())
    result = bounded_search(topology, drive, solver, benchmark)
    write_search(result, Path(args.output).resolve())
    print(json.dumps(result["selected"], indent=2))
    print(f"search_output={Path(args.output).name}")


def _search_delay(args: argparse.Namespace) -> None:
    topology, drive, solver, benchmark, _ = load_config(Path(args.config).resolve())
    result = bounded_delay_search(topology, drive, solver, benchmark)
    write_delay_search(result, Path(args.output).resolve())
    print(json.dumps(result["selected"], indent=2))
    print(f"delay_search_output={Path(args.output).name}")


def _validate_fdtd(args: argparse.Namespace) -> None:
    write_validation(Path(args.source).resolve(), Path(args.output).resolve())
    print(f"fdtd_validation={Path(args.output).name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="photonic-reservoir", description="Legacy three-ring commands; active P1 has a separate workspace")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="run the fixed ablation matrix")
    run_parser.add_argument("--config", required=True)
    run_parser.add_argument("--project-dir", default=str(Path(__file__).resolve().parents[2]))
    run_parser.add_argument("--candidate-lock", help="required only for the frozen P0 blind seed suite")
    run_parser.set_defaults(func=_run)
    evidence_parser = subparsers.add_parser("evidence", help="hash the immutable legacy evidence")
    evidence_parser.add_argument("--source", required=True)
    evidence_parser.add_argument("--output", default="legacy-three-ring/evidence/legacy_tidy3d_manifest.json")
    evidence_parser.set_defaults(func=_evidence)
    search_parser = subparsers.add_parser("search", help="validation-only bounded three-ring search")
    search_parser.add_argument("--config", required=True)
    search_parser.add_argument("--output", default="legacy-three-ring/runs/search_narma10.json")
    search_parser.set_defaults(func=_search)
    delay_parser = subparsers.add_parser("search-delay", help="validation-only explicit feedback search")
    delay_parser.add_argument("--config", required=True)
    delay_parser.add_argument("--output", default="legacy-three-ring/runs/search_delay_narma10.json")
    delay_parser.set_defaults(func=_search_delay)
    validation_parser = subparsers.add_parser("validate-fdtd", help="audit existing static and transient FDTD evidence")
    validation_parser.add_argument("--source", required=True)
    validation_parser.add_argument("--output", default="legacy-three-ring/evidence/legacy_fdtd_validation.json")
    validation_parser.set_defaults(func=_validate_fdtd)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)
