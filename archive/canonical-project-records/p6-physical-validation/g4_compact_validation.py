"""Deterministic G4 phase-control, receiver, and thermal validation record."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from component_model import build_report, load_config, validate_architecture


HERE = Path(__file__).resolve().parent
CONFIG = HERE / "configs" / "baseline-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_g4_record() -> dict[str, Any]:
    config = load_config(CONFIG)
    validate_architecture(config)
    report = build_report(config, check_provenance=True)
    arch = config["architecture"]
    phase = config["phase_and_receiver"]
    thermal = config["thermal_envelope"]
    optical = config["optical_power"]

    slot_rate = float(arch["symbol_rate_hz"]) * int(arch["time_multiplex_slots"])
    thermal_bw = float(phase["thermal_control_bandwidth_hz_assumption"])
    switching_period_s = 1.0 / slot_rate
    max_delay_s = float(report["coherence"]["maximum_differential_delay_s"])
    phase_rms_rad = math.radians(float(phase["dynamic_phase_jitter_limit_deg_rms"]))
    linewidth_allocation_hz = phase_rms_rad**2 / (2.0 * math.pi * max_delay_s)

    responsivity = float(phase["pd_responsivity_min_a_per_w"])
    lo_mw = float(optical["lo_power_mw_per_lo_arm"])
    signal_peak_mw = float(optical["signal_scale_mw_at_u_equal_1"]) * float(optical["input_field_max"]) ** 2
    constructive_power_mw = 0.5 * (math.sqrt(lo_mw) + math.sqrt(signal_peak_mw)) ** 2
    destructive_power_mw = 0.5 * (math.sqrt(lo_mw) - math.sqrt(signal_peak_mw)) ** 2

    p_pi = float(thermal["phase_shifter_p_pi_mw_assumption"])
    trim_count = int(phase["thermal_trim_count"])
    crosstalk_multiplier = 1.0 + float(thermal["thermal_crosstalk_margin_fraction"])
    global_mw = float(thermal["global_stabilization_power_mw_assumption"])
    average_mw = trim_count * p_pi * float(thermal["mean_abs_phase_fraction_of_pi"]) * crosstalk_multiplier + global_mw
    maximum_mw = trim_count * p_pi * crosstalk_multiplier + global_mw
    limit_mw = float(thermal["heater_power_limit_mw"])

    physical_gates = {
        "routing_schedule_10pd_x_3slot": "PASS",
        "thermal_not_used_for_30ghz_routing": "PASS" if thermal_bw < slot_rate else "FAIL",
        "fast_eo_switch_s_parameter_and_bandwidth": "OPEN",
        "laser_linewidth_with_shared_phase_budget": "OPEN",
        "phase_shifter_p_pi_l_and_insertion": "OPEN",
        "thermal_time_constant": "OPEN",
        "thermal_crosstalk_matrix": "OPEN",
        "pd_50ghz_responsivity_noise": "OPEN",
        "pd_tia_linearity_at_required_current": "OPEN",
    }
    return {
        "name": "p6-g4-compact-validation-v1",
        "source_sha256": sha256(Path(__file__)),
        "config_sha256": sha256(CONFIG),
        "p5_blind_rerun": False,
        "routing": {
            "pd_count": int(arch["parallel_pd_count"]),
            "slot_count": int(arch["time_multiplex_slots"]),
            "slot_rate_hz": slot_rate,
            "slot_period_s": switching_period_s,
            "required_technology": "fast_EO_or_switch",
            "thermal_trim_role": "static_drift_and_fabrication_offset_only",
        },
        "phase": {
            "maximum_coherent_differential_delay_s": max_delay_s,
            "dynamic_phase_limit_deg_rms": float(phase["dynamic_phase_jitter_limit_deg_rms"]),
            "laser_linewidth_hz_if_entire_dynamic_budget_is_laser": linewidth_allocation_hz,
            "interpretation": "upper bound before pilot, feedback, and thermal-noise allocations",
        },
        "receiver": {
            "p5_compatibility_bandwidth_hz": float(phase["pd_bandwidth_p5_compatibility_hz"]),
            "responsivity_floor_a_per_w": responsivity,
            "input_noise_ceiling_a_per_sqrt_hz": float(phase["pd_input_noise_max_a_per_sqrt_hz"]),
            "lo_arm_power_mw": lo_mw,
            "encoded_signal_peak_power_mw": signal_peak_mw,
            "ideal_combiner_constructive_output_mw": constructive_power_mw,
            "ideal_combiner_destructive_output_mw": destructive_power_mw,
            "required_linear_photocurrent_peak_a_at_responsivity_floor": responsivity * constructive_power_mw * 1e-3,
            "lo_only_photocurrent_a": responsivity * 0.5 * lo_mw * 1e-3,
            "saturation_and_tia_swing_evidence": "OPEN_PDK_OR_MEASUREMENT",
        },
        "thermal": {
            "trim_count": trim_count,
            "p_pi_mw_assumption": p_pi,
            "thermal_control_bandwidth_hz_assumption": thermal_bw,
            "thermal_to_slot_rate_ratio": thermal_bw / slot_rate,
            "average_heater_power_mw_assumption": average_mw,
            "maximum_heater_power_mw_assumption": maximum_mw,
            "heater_power_limit_mw": limit_mw,
            "maximum_headroom_mw_assumption": limit_mw - maximum_mw,
            "evidence": "ASSUMPTION_ONLY_REQUIRES_PDK_THERMAL_SOLVE_OR_MEASUREMENT",
        },
        "gates": physical_gates,
        "model_semantics_passed": all(physical_gates[k] == "PASS" for k in ("routing_schedule_10pd_x_3slot", "thermal_not_used_for_30ghz_routing")),
        "g4_physical_accepted": all(value == "PASS" for value in physical_gates.values()),
    }


if __name__ == "__main__":
    print(json.dumps(build_g4_record(), indent=2, ensure_ascii=False))
