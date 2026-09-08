"""Robust development-only optimization across data and hardware realizations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ..benchmark import delayed_input_features, generate_narma
from ..p1_coherent_delay.ideal import fast_validation_nmse
from ..p2_architecture.screen import _benchmark
from ..p3_realistic.screen import architecture_feasibility, physical_sparse_features
from ..protocol import dataset_sha256, source_tree_sha256


def _summary(rows: list[dict[str, Any]], data_seeds: tuple[int, ...], threshold: float, robust_count: int) -> dict[str, Any]:
    values = np.asarray([row["validation_nmse"] for row in rows], dtype=float)
    per_data_seed = {
        str(seed): float(np.median([row["validation_nmse"] for row in rows if row["data_seed"] == seed]))
        for seed in data_seeds
    }
    seed_values = np.asarray(list(per_data_seed.values()), dtype=float)
    run_fraction = float(np.mean(values <= 0.05))
    seed_count = int(np.sum(seed_values <= 0.05))
    return {
        "median_validation_nmse": float(np.median(values)),
        "p90_validation_nmse": float(np.quantile(values, 0.90)),
        "max_validation_nmse": float(np.max(values)),
        "fraction_runs_at_or_below_0_05": run_fraction,
        "data_seed_medians": per_data_seed,
        "data_seeds_at_or_below_0_05": seed_count,
        "passed": bool(float(np.median(values)) <= threshold and seed_count >= robust_count and run_fraction >= 0.8),
    }


def evaluate_candidate(
    data: dict[int, tuple[np.ndarray, np.ndarray]],
    labels: list[str],
    physical: dict[str, Any],
    parallel_ports: int,
    hardware_seeds: tuple[int, ...],
    benchmark: Any,
    threshold: float,
    robust_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for hardware_seed in hardware_seeds:
        for data_seed, (delayed, target) in data.items():
            mixed_seed = int(hardware_seed) * 1_000_003 + int(data_seed)
            features = physical_sparse_features(delayed, labels, physical, parallel_ports, mixed_seed)
            result = fast_validation_nmse(features, target, benchmark)
            rows.append({
                "data_seed": int(data_seed),
                "hardware_seed": int(hardware_seed),
                "validation_nmse": result.validation_nmse,
                "best_alpha": result.best_alpha,
            })
    return rows, _summary(rows, benchmark.seeds, threshold, robust_count)


def run_optimization(protocol: dict[str, Any], p2_result: dict[str, Any], p3_config: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    benchmark = _benchmark(protocol, tuple(float(value) for value in config["ridge_alphas"]))
    n_lags = int(p2_result["n_lags"])
    ranking_labels = list(p2_result["channel_ranking_labels"])
    data: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        if dataset_sha256(u, target) != protocol["development"]["dataset_sha256"][str(seed)]:
            raise ValueError(f"development dataset commitment mismatch for seed {seed}")
        data[seed] = (delayed_input_features(u, n_lags), target)

    base = dict(p3_config["physical_profiles"][config["base_profile"]])
    hardware_seeds = tuple(int(seed) for seed in config["hardware_seeds"])
    candidates: list[dict[str, Any]] = []
    for channels in (int(value) for value in config["channel_budgets"]):
        labels = ranking_labels[:channels]
        for ports in (int(value) for value in config["parallel_port_counts"] if int(value) <= channels):
            for signal_power in (float(value) for value in config["signal_power_mw_per_port"]):
                for lo_ratio in (float(value) for value in config["lo_to_signal_power_ratios"]):
                    for noise_factor in (float(value) for value in config["receiver_noise_bandwidth_factors"]):
                        physical = dict(base)
                        physical["signal_power_mw"] = signal_power
                        physical["lo_power_mw"] = signal_power * lo_ratio
                        physical["receiver_noise_bandwidth_factor"] = noise_factor
                        total_power = ports * (physical["signal_power_mw"] + physical["lo_power_mw"])
                        feasibility = architecture_feasibility(channels, ports, n_lags, physical)
                        feasibility["estimated_total_optical_power_mw"] = total_power
                        feasibility["checks"]["total_optical_power"] = total_power <= float(config["max_total_optical_power_mw"])
                        feasibility["passed"] = all(feasibility["checks"].values())
                        rows, summary = evaluate_candidate(
                            data, labels, physical, ports, hardware_seeds, benchmark,
                            float(config["median_gate"]), int(config["robust_seed_count"]),
                        )
                        candidates.append({
                            "channels": channels,
                            "parallel_ports": ports,
                            "time_multiplex_steps": feasibility["time_multiplex_steps"],
                            "signal_power_mw_per_port": signal_power,
                            "lo_power_mw_per_port": signal_power * lo_ratio,
                            "receiver_noise_bandwidth_factor": noise_factor,
                            "hardware_realizations": len(hardware_seeds),
                            "feasibility": feasibility,
                            "summary": summary,
                            "scores": rows,
                            "selected_channel_labels": labels,
                            "passed": bool(feasibility["passed"] and summary["passed"]),
                        })

    passing = [candidate for candidate in candidates if candidate["passed"]]
    selected = min(
        passing,
        key=lambda item: (
            item["parallel_ports"], item["feasibility"]["estimated_total_optical_power_mw"],
            item["channels"], item["time_multiplex_steps"], item["summary"]["median_validation_nmse"],
        ),
    ) if passing else None
    return {
        "claim_level": "P4 development-only hardware-robust optimization; blind test remains sealed",
        "development_only": True,
        "test_evaluations": 0,
        "p0_protocol_sha256": protocol["protocol_sha256"],
        "source_sha256": source_tree_sha256(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "hardware_seeds": list(hardware_seeds),
        "candidates": candidates,
        "phase": config["phase"],
        "selected_candidate": selected,
        "optimization_found_candidate": selected is not None,
        "p4_gate_passed": bool(selected is not None and config["phase"] == "confirmation" and len(hardware_seeds) >= 5),
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
