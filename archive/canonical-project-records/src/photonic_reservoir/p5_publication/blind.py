"""One-shot P5 blind evaluation after an exact candidate lock."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ..benchmark import delayed_input_features, evaluate_features, generate_narma, paired_bootstrap_ci
from ..config import BenchmarkConfig
from ..p1_coherent_delay.ideal import coherent_square_law_features
from ..p3_realistic.screen import physical_sparse_features
from ..protocol import canonical_sha256, dataset_sha256, require_blind_authorization, source_tree_sha256
from .preflight import no_photonic_core_features


def _benchmark(protocol: dict[str, Any], alphas: tuple[float, ...]) -> BenchmarkConfig:
    suite = protocol["publication_blind"]
    split = suite["split"]
    return BenchmarkConfig(
        order=int(protocol["task"]["order"]), n_washout=int(split["washout"]),
        n_train=int(split["train"]), n_validation=int(split["validation"]), n_test=int(split["test"]),
        seeds=tuple(int(seed) for seed in suite["seeds"]), ridge_alphas=alphas,
    )


def _prediction_sha256(target: np.ndarray, prediction: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(target, dtype="<f8").tobytes())
    digest.update(np.ascontiguousarray(prediction, dtype="<f8").tobytes())
    return digest.hexdigest()


def run_blind(
    protocol: dict[str, Any], p2_result: dict[str, Any], p3_config: dict[str, Any],
    candidate: dict[str, Any], lock: dict[str, Any], lock_path: Path,
) -> dict[str, Any]:
    require_blind_authorization(protocol, lock_path)
    candidate_hash = canonical_sha256(candidate)
    if lock["candidate_config_sha256"] != candidate_hash:
        raise PermissionError("candidate config does not match the lock")
    if lock["source_sha256"] != source_tree_sha256():
        raise PermissionError("source tree changed after candidate lock")
    benchmark = _benchmark(protocol, tuple(float(value) for value in candidate["ridge_alphas"]))
    n_lags = int(candidate["n_lags"])
    count = int(candidate["channel_count"])
    indices = np.asarray(p2_result["channel_ranking"][:count], dtype=int)
    labels = list(p2_result["channel_ranking_labels"][:count])
    physical = dict(p3_config["physical_profiles"][candidate["physical_profile"]])
    physical.update(candidate["physical_overrides"])
    variants = ("photonic_candidate", "delayed_input", "same_delay_digital", "no_photonic_core")
    scores: dict[str, dict[int, float]] = {name: {} for name in variants}
    rows: list[dict[str, Any]] = []
    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        if dataset_sha256(u, target) != protocol["publication_blind"]["dataset_sha256"][str(seed)]:
            raise ValueError(f"blind dataset commitment mismatch for seed {seed}")
        delayed = delayed_input_features(u, n_lags)
        feature_sets = {
            "photonic_candidate": physical_sparse_features(delayed, labels, physical, int(candidate["parallel_ports"]), int(candidate["hardware_seed"]) * 1_000_003 + seed),
            "delayed_input": delayed,
            "same_delay_digital": coherent_square_law_features(delayed)[:, indices],
            "no_photonic_core": no_photonic_core_features(u),
        }
        for name, features in feature_sets.items():
            metric = evaluate_features(features, target, benchmark)
            if not np.isfinite(metric.test_nmse) or not np.all(np.isfinite(metric.prediction)):
                raise ValueError(f"non-finite blind result for seed {seed}, variant {name}")
            scores[name][seed] = metric.test_nmse
            rows.append({
                "seed": seed, "variant": name, "best_alpha": metric.best_alpha,
                "validation_nmse": metric.validation_nmse, "test_nmse": metric.test_nmse,
                "test_rmse": metric.test_rmse, "test_correlation": metric.test_correlation,
                "prediction_sha256": _prediction_sha256(metric.target, metric.prediction),
            })

    medians = {name: float(np.median(list(values.values()))) for name, values in scores.items()}
    candidate_values = np.asarray(list(scores["photonic_candidate"].values()))
    gates = protocol["publication_blind"]["success_gates"]
    control_results: dict[str, Any] = {}
    controls_pass = True
    for name in gates["required_superiority_controls"]:
        differences = np.asarray([scores["photonic_candidate"][seed] - scores[name][seed] for seed in benchmark.seeds])
        ci = paired_bootstrap_ci(differences, seed=int(candidate["bootstrap_seed"]), samples=int(candidate["bootstrap_samples"]))
        gain = (medians[name] - medians["photonic_candidate"]) / medians[name]
        passed = bool(gain >= float(gates["relative_gain_vs_each_superiority_control"]["threshold"]) and ci[1] < 0.0)
        control_results[name] = {"median_test_nmse": medians[name], "relative_gain": float(gain), "paired_difference_ci95": list(ci), "passed": passed}
        controls_pass = controls_pass and passed
    median_pass = bool(medians["photonic_candidate"] < float(gates["median_test_nmse"]["threshold"]))
    seed_count = int(np.sum(candidate_values < 0.05))
    count_pass = bool(seed_count >= int(gates["seed_count_below_0_05"]["threshold"]))
    return {
        "claim_level": "one-shot P5 blind publication evaluation; system-level physical model",
        "protocol_id": protocol["protocol_id"], "protocol_sha256": protocol["protocol_sha256"],
        "candidate_config_sha256": candidate_hash, "source_sha256": source_tree_sha256(),
        "candidate_lock_sha256": hashlib.sha256(lock_path.read_bytes()).hexdigest(),
        "blind_datasets_evaluated": len(benchmark.seeds), "test_evaluations": len(rows),
        "rows": rows,
        "summary": {
            "median_test_nmse": medians,
            "photonic_seed_count_below_0_05": seed_count,
            "median_gate_passed": median_pass, "seed_count_gate_passed": count_pass,
            "superiority_controls": control_results,
            "same_delay_digital_reference": {
                "median_test_nmse": medians["same_delay_digital"],
                "candidate_relative_penalty": float((medians["photonic_candidate"] - medians["same_delay_digital"]) / medians["same_delay_digital"]),
            },
            "publication_passed": bool(median_pass and count_pass and controls_pass),
        },
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
