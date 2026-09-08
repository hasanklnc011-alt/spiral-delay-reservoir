"""LEGACY: three-ring ablations and historical <0.30 publication gates."""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from .benchmark import delayed_input_features, esn_features, evaluate_features, generate_narma, mean_baseline, paired_bootstrap_ci
from .config import BenchmarkConfig, DriveConfig, FeedbackParams, RingParams, SolverConfig, TopologyParams, physical_validity, topology_from_dict
from .model import simulate
from .protocol import guard_reserved_blind_seeds


def _metric_dict(metric: Any) -> dict[str, float]:
    return {
        "best_alpha": metric.best_alpha,
        "validation_nmse": metric.validation_nmse,
        "test_nmse": metric.test_nmse,
        "test_rmse": metric.test_rmse,
        "test_correlation": metric.test_correlation,
    }


def _single_ring(topology: TopologyParams) -> TopologyParams:
    return TopologyParams(rings=(topology.rings[0],), coupling_linewidths=(), coupling_phases_rad=(), kerr_enabled=False)


def _uncoupled(topology: TopologyParams) -> TopologyParams:
    return replace(topology, coupling_linewidths=(0.0,) * (len(topology.rings) - 1), kerr_enabled=False)


def run_ablation(
    topology: TopologyParams,
    drive: DriveConfig,
    solver: SolverConfig,
    benchmark: BenchmarkConfig,
    feedback: FeedbackParams = FeedbackParams(),
    candidate_lock_path: Path | None = None,
    candidate_config_sha256: str | None = None,
) -> dict[str, Any]:
    guard_reserved_blind_seeds(benchmark.seeds, candidate_lock_path, candidate_config_sha256)
    rows: list[dict[str, Any]] = []
    predictions: dict[str, dict[str, list[float]]] = {}
    kerr_off = replace(topology, kerr_enabled=False)
    variants = {
        "three_ring_physical_kerr": (topology, drive, feedback),
        "three_ring_kerr_off": (kerr_off, drive, feedback),
        "three_ring_coherent_equal_features": (kerr_off, replace(drive, n_virtual=max(1, drive.n_virtual // 2), observation="coherent_field"), feedback),
        "three_ring_uncoupled": (_uncoupled(topology), drive, feedback),
        "three_ring_memory_reset": (kerr_off, replace(drive, reset_each_symbol=True), feedback),
        "single_ring": (_single_ring(topology), drive, feedback),
    }
    if feedback.enabled:
        # three_ring_memory_reset clears the ring state but leaves the delay line
        # intact, so on its own it cannot separate intrinsic cavity memory from
        # external echo memory. These two complete that control.
        variants["three_ring_delay_reset"] = (kerr_off, drive, replace(feedback, reset_each_symbol=True))
        variants["three_ring_full_memory_reset"] = (kerr_off, replace(drive, reset_each_symbol=True), replace(feedback, reset_each_symbol=True))

    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        baseline_sets = {
            "mean": mean_baseline(target, benchmark),
            "input_only": evaluate_features(u[:, None], target, benchmark),
            "delayed_input": evaluate_features(delayed_input_features(u, benchmark.order), target, benchmark),
            "digital_esn": evaluate_features(esn_features(u, benchmark.esn_state_dim, seed + 10_000), target, benchmark),
        }
        for name, metric in baseline_sets.items():
            rows.append({"seed": seed, "variant": name, **_metric_dict(metric), "diverged": False})
        for name, (variant_topology, variant_drive, variant_feedback) in variants.items():
            result = simulate(u, variant_topology, variant_drive, solver, variant_feedback)
            metric = evaluate_features(result.features, target, benchmark)
            rows.append({"seed": seed, "variant": name, **_metric_dict(metric), "diverged": result.diverged, "dt_s": result.dt_s, "substeps_per_node": result.substeps_per_node})
            predictions[f"{seed}:{name}"] = {"target": metric.target.tolist(), "prediction": metric.prediction.tolist()}

    summary = summarize_gates(rows, benchmark)
    return {"rows": rows, "summary": summary, "predictions": predictions}


def summarize_gates(rows: list[dict[str, Any]], benchmark: BenchmarkConfig) -> dict[str, Any]:
    grouped: dict[str, list[float]] = {}
    by_seed: dict[tuple[int, str], float] = {}
    for row in rows:
        grouped.setdefault(row["variant"], []).append(float(row["test_nmse"]))
        by_seed[(int(row["seed"]), row["variant"])] = float(row["test_nmse"])
    medians = {name: float(np.median(values)) for name, values in grouped.items()}
    seeds = sorted({seed for seed, _ in by_seed})
    system_name = "three_ring_physical_kerr"
    delayed_diffs = np.array([by_seed[(seed, system_name)] - by_seed[(seed, "delayed_input")] for seed in seeds])
    kerr_diffs = np.array([by_seed[(seed, system_name)] - by_seed[(seed, "three_ring_kerr_off")] for seed in seeds])
    delayed_ci = paired_bootstrap_ci(delayed_diffs)
    kerr_ci = paired_bootstrap_ci(kerr_diffs)
    wins = int(np.sum(delayed_diffs < 0))
    baseline_median = medians["delayed_input"]
    system_median = medians[system_name]
    relative_gain = (baseline_median - system_median) / baseline_median if baseline_median else float("nan")
    system_gate = system_median < 0.30 and relative_gain >= 0.10 and wins >= int(np.ceil(0.8 * len(seeds))) and delayed_ci[1] < 0
    kerr_off_median = medians["three_ring_kerr_off"]
    kerr_gain = (kerr_off_median - system_median) / kerr_off_median if kerr_off_median else float("nan")
    kerr_gate = kerr_gain >= 0.10 and kerr_ci[1] < 0
    protocol_complete = len(benchmark.seeds) >= 10 and benchmark.n_train >= 6000 and benchmark.n_validation >= 2000 and benchmark.n_test >= 3000
    return {
        "benchmark_order": benchmark.order,
        "publication_protocol_complete": protocol_complete,
        "median_test_nmse": medians,
        "system_vs_delayed_input": {"paired_difference_ci95": delayed_ci, "wins": wins, "relative_gain": relative_gain, "passed": bool(system_gate)},
        "physical_kerr_advantage": {"paired_difference_ci95": kerr_ci, "relative_gain": kerr_gain, "passed": bool(kerr_gate)},
        "fdtd_cloud_gate_open": bool(system_gate and benchmark.order == 10 and protocol_complete),
        "fdtd_gate_note": "Cloud validation requires the complete 10-seed NARMA-10 publication protocol." if benchmark.order != 10 or not protocol_complete else "Complete NARMA-10 publication gate controls cloud validation.",
    }


def _git_commit(project_root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(project_root), "rev-parse", "HEAD"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _git_worktree_dirty(project_root: Path) -> bool | None:
    """A commit alone does not pin the code that ran; uncommitted edits must show."""
    try:
        return bool(subprocess.check_output(["git", "-C", str(project_root), "status", "--porcelain"], text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _source_sha256() -> str | None:
    """Hash the package that actually ran, so two runs on one commit stay distinguishable."""
    package = Path(__file__).resolve().parent
    try:
        digest = hashlib.sha256()
        for path in sorted(package.rglob("*.py")):
            digest.update(path.relative_to(package).as_posix().encode())
            digest.update(path.read_bytes())
        return digest.hexdigest()[:16]
    except OSError:
        return None


def _validity_of(configs: dict[str, Any]) -> dict[str, Any] | None:
    """Record whether the drive stayed inside the FDTD-calibrated band."""
    try:
        return physical_validity(topology_from_dict(configs["topology"]), DriveConfig(**configs["drive"]))
    except (KeyError, TypeError, ValueError):
        return None


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    # bool must precede int: bool is an int subclass, so the int branch would
    # otherwise serialise True as 1.
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return number if np.isfinite(number) else None
    if isinstance(value, (int, np.integer)):
        return int(value)
    return value


def write_run(output_root: Path, payload: dict[str, Any], configs: dict[str, Any], project_root: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256(json.dumps(configs, sort_keys=True, default=str).encode()).hexdigest()[:10]
    run_dir = output_root / f"{timestamp}_{digest}"
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "created_utc": timestamp,
        "git_commit": _git_commit(project_root),
        "git_worktree_dirty": _git_worktree_dirty(project_root),
        "source_sha256": _source_sha256(),
        "claim_level": "TCMT",
        "physical_validity": _validity_of(configs),
        "fdtd_dynamic_validation": False,
        "configuration_sha256": digest,
        "configs": configs,
    }
    (run_dir / "manifest.json").write_text(json.dumps(_json_safe(manifest), indent=2, allow_nan=False), encoding="utf-8")
    (run_dir / "metrics.json").write_text(json.dumps(_json_safe({"rows": payload["rows"], "summary": payload["summary"]}), indent=2, allow_nan=False), encoding="utf-8")
    (run_dir / "predictions.json").write_text(json.dumps(_json_safe(payload["predictions"]), allow_nan=False), encoding="utf-8")
    return run_dir
