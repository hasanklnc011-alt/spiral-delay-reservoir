"""Deterministic P6 component and budget model.

This module never imports or evaluates the P5 blind benchmark. It only verifies
the immutable P5 artefact hashes when explicitly requested.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


C_M_S = 299_792_458.0
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DEFAULT_CONFIG = HERE / "configs" / "baseline-v1.json"


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def verify_provenance(config: dict[str, Any]) -> dict[str, Any]:
    policy = config["blind_policy"]
    checks: dict[str, Any] = {
        "rerun_forbidden": policy["rerun_allowed"] is False,
        "blind_tuning_forbidden": policy["tuning_from_blind_allowed"] is False,
    }
    artifact_hash_fields = {
        "blind_result": "blind_result_sha256",
        "candidate_lock": "candidate_lock_sha256",
        "candidate_config": "candidate_config_file_sha256",
        "protocol": "protocol_file_sha256",
        "p4_confirmation": "p4_confirmation_sha256",
    }
    for key, hash_field in artifact_hash_fields.items():
        path = PROJECT_ROOT / policy[f"{key}_path"]
        actual = sha256_file(path) if path.is_file() else None
        expected = policy[hash_field]
        checks[f"{key}_exists"] = path.is_file()
        checks[f"{key}_sha256_matches"] = actual == expected
        checks[f"{key}_actual_sha256"] = actual

    lock = json.loads((PROJECT_ROOT / policy["candidate_lock_path"]).read_text(encoding="utf-8"))
    candidate = json.loads((PROJECT_ROOT / policy["candidate_config_path"]).read_text(encoding="utf-8"))
    protocol = json.loads((PROJECT_ROOT / policy["protocol_path"]).read_text(encoding="utf-8"))
    p4 = json.loads((PROJECT_ROOT / policy["p4_confirmation_path"]).read_text(encoding="utf-8"))
    checks["candidate_config_canonical_matches"] = canonical_json_sha256(candidate) == policy["candidate_config_canonical_sha256"]
    checks["lock_candidate_config_matches"] = lock["candidate_config_sha256"] == policy["candidate_config_canonical_sha256"]
    checks["lock_protocol_matches"] = lock["protocol_sha256"] == policy["protocol_internal_sha256"]
    checks["lock_source_matches_frozen_value"] = lock["source_sha256"] == "a0e6561a726a6d17a31dd1bde37257435f857549cb726d711bea6e5c4a17a080"
    checks["protocol_internal_hash_matches"] = protocol["protocol_sha256"] == policy["protocol_internal_sha256"]
    checks["routing_labels_match_p4"] = list(config["architecture"]["channel_labels"]) == list(p4["selected_candidate"]["selected_channel_labels"])
    checks["passed"] = all(value for name, value in checks.items() if name.endswith(("forbidden", "exists", "matches")))
    return checks


def parse_label(label: str) -> tuple[str, tuple[int, ...]]:
    family, raw = label.split(":", 1)
    indices = tuple(int(item) for item in raw.split(","))
    expected = {"self": 1, "lo": 1, "pair": 2}
    if family not in expected or len(indices) != expected[family]:
        raise ValueError(f"invalid channel label: {label}")
    return family, indices


def validate_architecture(config: dict[str, Any]) -> None:
    arch = config["architecture"]
    labels = arch["channel_labels"]
    if len(labels) != arch["channel_count"]:
        raise ValueError("channel label count differs from locked channel_count")
    if arch["channel_count"] != arch["parallel_pd_count"] * arch["time_multiplex_slots"]:
        raise ValueError("channel_count must equal PD count times slot count")
    used_taps: set[int] = set()
    for label in labels:
        _, indices = parse_label(label)
        used_taps.update(indices)
    if min(used_taps) != 0 or max(used_taps) != arch["n_lags"] - 1:
        raise ValueError("locked channels do not span the full delay-tap range")


def delay_metrics(config: dict[str, Any], *, group_index: float | None = None) -> dict[str, float]:
    arch = config["architecture"]
    ng = float(arch["group_index_target"] if group_index is None else group_index)
    target_s = (int(arch["n_lags"]) - 1) / float(arch["symbol_rate_hz"])
    required_cm = C_M_S * target_s / ng * 100.0
    locked_cm = float(arch["delay_length_cm_locked"])
    actual_s = ng * (locked_cm / 100.0) / C_M_S
    return {
        "group_index": ng,
        "target_delay_s": target_s,
        "required_length_cm": required_cm,
        "locked_length_cm": locked_cm,
        "delay_at_locked_length_s": actual_s,
        "symbols_at_locked_length": actual_s * float(arch["symbol_rate_hz"]),
        "relative_delay_error": abs(actual_s - target_s) / target_s,
    }


def _archimedean_arm_length(radius_inner_um: float, radius_outer_um: float, b_um: float) -> float:
    def primitive(radius: float) -> float:
        return 0.5 * (radius * math.hypot(radius, b_um) + b_um * b_um * math.asinh(radius / b_um)) / b_um

    return primitive(radius_outer_um) - primitive(radius_inner_um)


def spiral_estimate(config: dict[str, Any]) -> dict[str, float]:
    layout = config["layout_envelope"]
    length_um = float(config["architecture"]["delay_length_cm_locked"]) * 10_000.0
    pitch = float(layout["lane_pitch_um"])
    radius_inner = float(layout["minimum_bend_radius_um"])
    # Each of the two interleaved arms advances by two lane pitches per turn.
    b_um = pitch / math.pi
    turnaround_um = math.pi * radius_inner

    def total_length(radius_outer: float) -> float:
        return 2.0 * _archimedean_arm_length(radius_inner, radius_outer, b_um) + turnaround_um

    low = radius_inner
    high = max(2.0 * radius_inner, radius_inner + pitch)
    while total_length(high) < length_um:
        high *= 2.0
    for _ in range(100):
        middle = 0.5 * (low + high)
        if total_length(middle) < length_um:
            low = middle
        else:
            high = middle
    radius_outer = 0.5 * (low + high)
    turns_per_arm = (radius_outer - radius_inner) / (2.0 * pitch)
    total_bend_angle_rad = 4.0 * math.pi * turns_per_arm + math.pi
    equivalent_90 = total_bend_angle_rad / (0.5 * math.pi)
    margin = float(layout["keepout_margin_um"])
    side_um = 2.0 * (radius_outer + margin)
    bend_loss_db = equivalent_90 * float(layout["bend_loss_db_per_90deg_assumption"])
    return {
        "model": "interleaved double Archimedean estimate; not GDS",
        "centerline_length_um": length_um,
        "inner_radius_um": radius_inner,
        "outer_radius_um": radius_outer,
        "turns_per_arm": turns_per_arm,
        "equivalent_90deg_bends": equivalent_90,
        "bend_loss_db_assumption": bend_loss_db,
        "keepout_side_um": side_um,
        "keepout_area_mm2": side_um * side_um * 1e-6,
    }


def slot_power_metrics(config: dict[str, Any]) -> list[dict[str, float | int]]:
    arch = config["architecture"]
    optical = config["optical_power"]
    labels = list(arch["channel_labels"])
    per_slot = int(arch["parallel_pd_count"])
    signal_scale = float(optical["signal_scale_mw_at_u_equal_1"])
    input_peak = float(optical["input_field_max"])
    lo_power = float(optical["lo_power_mw_per_lo_arm"])
    output: list[dict[str, float | int]] = []
    for slot in range(int(arch["time_multiplex_slots"])):
        signal_arms = 0
        lo_arms = 0
        for label in labels[slot * per_slot : (slot + 1) * per_slot]:
            family, _ = parse_label(label)
            signal_arms += 2 if family == "pair" else 1
            lo_arms += 1 if family == "lo" else 0
        normalized = signal_arms * signal_scale + lo_arms * lo_power
        encoded = signal_arms * signal_scale * input_peak**2 + lo_arms * lo_power
        output.append({
            "slot": slot,
            "signal_arm_uses": signal_arms,
            "lo_arm_uses": lo_arms,
            "normalized_arm_power_mw_at_u_equal_1": normalized,
            "encoded_peak_arm_power_mw_at_u_max": encoded,
        })
    return output


def routing_metrics(config: dict[str, Any]) -> dict[str, Any]:
    """Return the exact 10-PD x 3-slot schedule and per-slot tap multicast."""
    arch = config["architecture"]
    labels = list(arch["channel_labels"])
    pd_count = int(arch["parallel_pd_count"])
    slots = int(arch["time_multiplex_slots"])
    matrix = [[labels[slot * pd_count + pd] for slot in range(slots)] for pd in range(pd_count)]
    fanouts: list[dict[str, Any]] = []
    maximum = 0
    for slot in range(slots):
        counts: dict[int, int] = {}
        for label in labels[slot * pd_count : (slot + 1) * pd_count]:
            _, indices = parse_label(label)
            for tap in indices:
                counts[tap] = counts.get(tap, 0) + 1
        maximum = max(maximum, max(counts.values()))
        fanouts.append({"slot": slot, "tap_fanout": {str(key): value for key, value in sorted(counts.items())}})
    return {
        "pd_by_slot": matrix,
        "per_slot_tap_fanout": fanouts,
        "maximum_same_slot_tap_fanout": maximum,
        "maximum_intentional_multicast_division_db": 10.0 * math.log10(maximum),
    }


def coherence_metrics(config: dict[str, Any]) -> dict[str, float]:
    arch = config["architecture"]
    max_delta_symbols = 0
    for label in arch["channel_labels"]:
        family, indices = parse_label(label)
        if family == "pair":
            delta = abs(indices[1] - indices[0])
        elif family == "lo":
            delta = indices[0]
        else:
            delta = 0
        max_delta_symbols = max(max_delta_symbols, delta)
    max_delta_s = max_delta_symbols / float(arch["symbol_rate_hz"])
    sigma_rad = math.radians(float(config["phase_and_receiver"]["dynamic_phase_jitter_limit_deg_rms"]))
    linewidth_phase_budget_hz = sigma_rad**2 / (2.0 * math.pi * max_delta_s)
    linewidth_visibility_hz = -math.log(0.99) / (math.pi * max_delta_s)
    return {
        "maximum_differential_delay_symbols": float(max_delta_symbols),
        "maximum_differential_delay_s": max_delta_s,
        "laser_linewidth_hz_if_all_2deg_rms_budget": linewidth_phase_budget_hz,
        "laser_linewidth_hz_for_visibility_0_99": linewidth_visibility_hz,
    }


def ideal_combiner_output_power(power_a_mw: float, power_b_mw: float, phase_rad: float, *, excess_loss_db: float = 0.0) -> float:
    """One output of a passive ideal 3-dB combiner, including excess loss."""
    if power_a_mw < 0.0 or power_b_mw < 0.0:
        raise ValueError("optical powers must be non-negative")
    field_power = 0.5 * (power_a_mw + power_b_mw + 2.0 * math.sqrt(power_a_mw * power_b_mw) * math.cos(phase_rad))
    return field_power * 10.0 ** (-excess_loss_db / 10.0)


def receiver_metrics(config: dict[str, Any]) -> dict[str, float | str]:
    optical = config["optical_power"]
    receiver = config["phase_and_receiver"]
    responsivity = float(receiver["pd_responsivity_min_a_per_w"])
    lo_mw = float(optical["lo_power_mw_per_lo_arm"])
    signal_peak_mw = float(optical["signal_scale_mw_at_u_equal_1"]) * float(optical["input_field_max"]) ** 2
    lo_only_out_mw = ideal_combiner_output_power(0.0, lo_mw, 0.0)
    constructive_out_mw = ideal_combiner_output_power(signal_peak_mw, lo_mw, 0.0)
    return {
        "system_minimum_bandwidth_hz": float(receiver["pd_bandwidth_min_hz"]),
        "p5_model_compatibility_bandwidth_hz": float(receiver["pd_bandwidth_p5_compatibility_hz"]),
        "lo_only_current_before_combiner_a": responsivity * lo_mw * 1e-3,
        "lo_only_current_one_ideal_output_a": responsivity * lo_only_out_mw * 1e-3,
        "signal_lo_constructive_current_one_ideal_output_a": responsivity * constructive_out_mw * 1e-3,
        "pd_saturation_status": receiver["pd_saturation_status"],
        "combiner_passive_s_matrix_status": receiver["combiner_passive_s_matrix_status"],
    }


def loss_metrics(config: dict[str, Any], spiral: dict[str, float]) -> dict[str, Any]:
    loss = config["loss_envelope"]
    length_cm = float(config["architecture"]["delay_length_cm_locked"])
    propagation_db = length_cm * float(loss["propagation_loss_db_per_cm_assumption"])
    bend_db = float(spiral["bend_loss_db_assumption"])
    combined_per_cm = (propagation_db + bend_db) / length_cm
    tap_count = int(loss["signal_tap_count"])
    signal_sections = tap_count - 1
    lo_depth = math.ceil(math.log2(int(loss["lo_fanout_count"])))
    splitter_excess = float(loss["splitter_excess_loss_limit_db_per_stage"])
    tap_through_excess = float(loss["progressive_tap_through_excess_loss_db_per_cell_assumption"])
    return {
        "propagation_loss_db_assumption_at_max_delay": propagation_db,
        "bend_loss_db_assumption_at_max_delay": bend_db,
        "propagation_plus_bend_db_per_cm": combined_per_cm,
        "propagation_plus_bend_within_p5_stress_envelope": combined_per_cm <= float(loss["propagation_plus_bend_limit_db_per_cm"]),
        "signal_progressive_tap_sections": signal_sections,
        "signal_equal_tap_ideal_division_db": 10.0 * math.log10(tap_count),
        "signal_longest_path_tap_through_excess_db_assumption": signal_sections * tap_through_excess,
        "lossless_progressive_tap_kappa_power": [1.0 / remaining for remaining in range(tap_count, 0, -1)],
        "lo_tree_depth_lower_bound": lo_depth,
        "lo_ideal_division_db": 10.0 * math.log10(int(loss["lo_fanout_count"])),
        "lo_splitter_excess_db_bound": lo_depth * splitter_excess,
        "source_distribution_status": loss["source_distribution_status"],
    }


def thermal_metrics(config: dict[str, Any]) -> dict[str, float | int | bool | str]:
    thermal = config["thermal_envelope"]
    phase = config["phase_and_receiver"]
    count = int(phase["thermal_trim_count"])
    p_pi = float(thermal["phase_shifter_p_pi_mw_assumption"])
    fraction = float(thermal["mean_abs_phase_fraction_of_pi"])
    margin = 1.0 + float(thermal["thermal_crosstalk_margin_fraction"])
    global_power = float(thermal["global_stabilization_power_mw_assumption"])
    average = count * p_pi * fraction * margin + global_power
    maximum = count * p_pi * margin + global_power
    slot_rate = float(config["architecture"]["symbol_rate_hz"]) * int(config["architecture"]["time_multiplex_slots"])
    thermal_bw = float(phase["thermal_control_bandwidth_hz_assumption"])
    return {
        "thermal_trim_count": count,
        "slot_rate_hz": slot_rate,
        "thermal_control_bandwidth_hz_assumption": thermal_bw,
        "thermal_can_reconfigure_per_slot": thermal_bw >= slot_rate,
        "thermal_trim_role": phase["thermal_trim_role"],
        "heater_average_power_mw_assumption": average,
        "heater_maximum_power_mw_assumption": maximum,
        "heater_power_limit_mw": float(thermal["heater_power_limit_mw"]),
        "assumed_maximum_within_limit": maximum <= float(thermal["heater_power_limit_mw"]),
        "evidence_status": thermal["status"],
    }


def build_report(config: dict[str, Any], *, check_provenance: bool = False) -> dict[str, Any]:
    validate_architecture(config)
    delay = delay_metrics(config)
    legacy_ng = float(config["platform_gate"]["legacy_reference_only"]["group_index"])
    legacy_delay = delay_metrics(config, group_index=legacy_ng)
    spiral = spiral_estimate(config)
    losses = loss_metrics(config, spiral)
    powers = slot_power_metrics(config)
    thermal = thermal_metrics(config)
    routing = routing_metrics(config)
    coherence = coherence_metrics(config)
    receiver = receiver_metrics(config)
    tolerance = float(config["architecture"]["group_index_tolerance_fraction"])
    gates = {
        "p5_provenance": "PASS" if check_provenance and verify_provenance(config)["passed"] else ("NOT_CHECKED" if not check_provenance else "FAIL"),
        "group_index_mode_solve": "OPEN",
        "delay_at_target_group_index_arithmetic": "PASS" if delay["relative_delay_error"] <= tolerance else "FAIL",
        "spiral_gds_length_and_drc": "OPEN",
        "bend_em": "OPEN",
        "splitter_tap_em_and_power_mapping": "OPEN",
        "combiner_em": "OPEN",
        "fast_slot_routing": "OPEN",
        "phase_thermal": "OPEN",
        "photodiode": "OPEN",
        "full_link_composition": "OPEN",
    }
    return {
        "name": config["name"],
        "claim_level": config["claim_level"],
        "blind_policy": config["blind_policy"],
        "delay": delay,
        "legacy_reference_delay": legacy_delay,
        "spiral_floorplan": spiral,
        "loss": losses,
        "routing": routing,
        "slot_optical_power": powers,
        "coherence": coherence,
        "receiver": receiver,
        "thermal": thermal,
        "gates": gates,
        "p6_accepted": all(value == "PASS" for value in gates.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--check-provenance", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    print(json.dumps(build_report(config, check_provenance=args.check_provenance), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
