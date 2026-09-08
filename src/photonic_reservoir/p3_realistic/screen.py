"""Development-only P3 loss, noise, tolerance, and throughput screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from ..benchmark import delayed_input_features, generate_narma
from ..p1_coherent_delay.ideal import fast_validation_nmse
from ..p2_architecture.screen import _benchmark, _summarize
from ..protocol import dataset_sha256, source_tree_sha256

LIGHT_SPEED_M_S = 299_792_458.0
ELECTRON_CHARGE_C = 1.602_176_634e-19


def architecture_feasibility(channels: int, parallel_ports: int, n_lags: int, physical: dict[str, Any]) -> dict[str, Any]:
    if channels < 1 or parallel_ports < 1 or parallel_ports > channels:
        raise ValueError("invalid channel/port count")
    slots = int(np.ceil(channels / parallel_ports))
    symbol_rate = float(physical["symbol_rate_hz"])
    group_index = float(physical["group_index"])
    delay_length_cm = (n_lags - 1) * LIGHT_SPEED_M_S / group_index / symbol_rate * 100.0
    slot_rate = symbol_rate * slots
    required_bandwidth = 0.5 * slot_rate
    checks = {
        "delay_length": delay_length_cm <= float(physical["max_delay_length_cm"]),
        "detector_bandwidth": required_bandwidth <= float(physical["detector_bandwidth_hz"]),
        "switch_rate": slot_rate <= float(physical["max_switch_rate_hz"]),
    }
    return {
        "parallel_ports": parallel_ports,
        "time_multiplex_steps": slots,
        "symbol_rate_hz": symbol_rate,
        "slot_rate_hz": slot_rate,
        "required_detector_bandwidth_hz": required_bandwidth,
        "max_delay_length_cm": delay_length_cm,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _parse_label(label: str) -> tuple[str, int, int | None]:
    family, indices = label.split(":", 1)
    values = [int(value) for value in indices.split(",")]
    if family in {"self", "lo"} and len(values) == 1:
        return family, values[0], None
    if family == "pair" and len(values) == 2:
        return family, values[0], values[1]
    raise ValueError(f"invalid primitive channel label: {label}")


def _multiplex_filter(current: np.ndarray, parallel_ports: int, bandwidth_hz: float, symbol_rate_hz: float) -> np.ndarray:
    n_samples, channels = current.shape
    slots = int(np.ceil(channels / parallel_ports))
    if slots == 1:
        return current.copy()
    slot_period = 1.0 / (symbol_rate_hz * slots)
    alpha = 1.0 - np.exp(-2.0 * np.pi * bandwidth_hz * slot_period)
    output = np.empty_like(current)
    state = np.zeros(parallel_ports, dtype=float)
    for sample in range(n_samples):
        for slot in range(slots):
            start = slot * parallel_ports
            stop = min(start + parallel_ports, channels)
            width = stop - start
            state[:width] += alpha * (current[sample, start:stop] - state[:width])
            output[sample, start:stop] = state[:width]
    return output


def physical_sparse_features(
    delayed: np.ndarray,
    labels: list[str],
    physical: dict[str, Any],
    parallel_ports: int,
    seed: int,
) -> np.ndarray:
    values = np.asarray(delayed, dtype=float)
    if values.ndim != 2 or not np.all(np.isfinite(values)):
        raise ValueError("delayed fields must be a finite 2D array")
    rng = np.random.default_rng(seed)
    symbol_rate = float(physical["symbol_rate_hz"])
    length_per_lag_cm = LIGHT_SPEED_M_S / float(physical["group_index"]) / symbol_rate * 100.0
    lag = np.arange(values.shape[1], dtype=float)
    path_loss_db = (
        lag * length_per_lag_cm * float(physical["waveguide_loss_db_per_cm"])
        + float(physical["switch_insertion_loss_db"])
    )
    signal_amplitude = np.sqrt(float(physical["signal_power_mw"]) * 1e-3) * values
    signal_amplitude *= 10.0 ** (-path_loss_db[None, :] / 20.0)
    lo_amplitude = np.sqrt(float(physical["lo_power_mw"]) * 1e-3)
    static_phase = rng.normal(0.0, np.deg2rad(float(physical["static_phase_error_deg"])), len(labels))
    dynamic_phase = rng.normal(0.0, np.deg2rad(float(physical["dynamic_phase_jitter_deg"])), (len(values), len(labels)))
    lo_drift = 1.0 + rng.normal(0.0, float(physical["lo_amplitude_drift_fraction"]), (len(values), len(labels)))
    inactive_leakage = np.sum(signal_amplitude**2, axis=1) * 10.0 ** (-float(physical["extinction_ratio_db"]) / 10.0)
    detector_power = np.empty((len(values), len(labels)), dtype=float)
    for column, label in enumerate(labels):
        family, left, right = _parse_label(label)
        phase = static_phase[column] + dynamic_phase[:, column]
        if family == "self":
            power = np.abs(signal_amplitude[:, left]) ** 2
        elif family == "lo":
            field = signal_amplitude[:, left] + lo_amplitude * lo_drift[:, column] * np.exp(1j * phase)
            power = np.abs(field) ** 2
        else:
            field = signal_amplitude[:, left] + signal_amplitude[:, int(right)] * np.exp(1j * phase)
            power = np.abs(field) ** 2
        detector_power[:, column] = power + inactive_leakage
    detector_power *= 10.0 ** (-float(physical["combiner_insertion_loss_db"]) / 10.0)

    responsivity = float(physical["responsivity_a_per_w"])
    current = responsivity * detector_power
    detector_bandwidth = float(physical["detector_bandwidth_hz"])
    current = _multiplex_filter(current, parallel_ports, detector_bandwidth, symbol_rate)
    slots = int(np.ceil(len(labels) / parallel_ports))
    noise_bandwidth = min(
        detector_bandwidth,
        float(physical.get("receiver_noise_bandwidth_factor", 1.0)) * 0.5 * symbol_rate * slots,
    )
    shot_std = np.sqrt(np.maximum(2.0 * ELECTRON_CHARGE_C * current * noise_bandwidth, 0.0))
    thermal_std = float(physical["thermal_noise_a_per_sqrt_hz"]) * np.sqrt(noise_bandwidth)
    current += rng.normal(size=current.shape) * np.sqrt(shot_std**2 + thermal_std**2)
    if not np.all(np.isfinite(current)):
        raise ValueError("physical readout produced non-finite features")
    return current


def run_screen(protocol: dict[str, Any], p2_result: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    n_lags = int(p2_result["n_lags"])
    budgets = [int(value) for value in config["channel_budgets"]]
    benchmark = _benchmark(protocol, tuple(float(value) for value in config["ridge_alphas"]))
    ranking_labels = list(p2_result["channel_ranking_labels"])
    data: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for seed in benchmark.seeds:
        u, target = generate_narma(benchmark.n_total, benchmark.order, seed)
        if dataset_sha256(u, target) != protocol["development"]["dataset_sha256"][str(seed)]:
            raise ValueError(f"development dataset commitment mismatch for seed {seed}")
        data[seed] = (delayed_input_features(u, n_lags), target)

    candidates: list[dict[str, Any]] = []
    for profile_name, physical in config["physical_profiles"].items():
        for budget in budgets:
            labels = ranking_labels[:budget]
            for ports in (int(value) for value in config["parallel_port_counts"] if int(value) <= budget):
                feasibility = architecture_feasibility(budget, ports, n_lags, physical)
                scores = []
                for dataset_seed, (delayed, target) in data.items():
                    features = physical_sparse_features(
                        delayed, labels, physical, ports,
                        int(config["hardware_seed_base"]) + dataset_seed + 1009 * budget + 7919 * ports,
                    )
                    result = fast_validation_nmse(features, target, benchmark)
                    scores.append({"seed": dataset_seed, "validation_nmse": result.validation_nmse, "best_alpha": result.best_alpha})
                summary = _summarize(
                    scores, float(config["median_gate"]), float(config["robust_seed_threshold"]), int(config["robust_seed_count"])
                )
                candidates.append({
                    "profile": profile_name,
                    "channels": budget,
                    "parallel_ports": ports,
                    "time_multiplex_steps": feasibility["time_multiplex_steps"],
                    "feasibility": feasibility,
                    "summary": summary,
                    "scores": scores,
                    "selected_channel_labels": labels,
                    "passed": bool(feasibility["passed"] and summary["passed"]),
                })

    profile_order = {name: index for index, name in enumerate(config["physical_profiles"])}
    selection_profiles = set(config["selection_profiles"])
    passing = [candidate for candidate in candidates if candidate["passed"] and candidate["profile"] in selection_profiles]
    selected = min(
        passing,
        key=lambda item: (
            item["parallel_ports"], item["channels"], item["time_multiplex_steps"],
            profile_order[item["profile"]], item["summary"]["median_validation_nmse"],
        ),
    ) if passing else None
    return {
        "claim_level": "P3 system-level physical tolerance model; not component/FDTD validation",
        "development_only": True,
        "test_evaluations": 0,
        "p0_protocol_sha256": protocol["protocol_sha256"],
        "p2_result_sha256": hashlib.sha256(json.dumps(p2_result, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "source_sha256": source_tree_sha256(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "candidates": candidates,
        "selected_candidate": selected,
        "p3_gate_passed": selected is not None,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
