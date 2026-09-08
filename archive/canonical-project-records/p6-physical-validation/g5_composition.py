"""Fail-closed P6 full-link composition from accepted and open evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def read(relative: str) -> dict[str, Any]:
    return json.loads((HERE / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_g5_record() -> dict[str, Any]:
    baseline = read("configs/baseline-v1.json")
    g1 = read("configs/g1-accepted-v1.json")
    g2 = read("runs/g2-spiral-layout-result-v1.json")
    bend = read("runs/g3b-bend-r10-deembedded-fine-convergence-v1.json")
    g3c = read("runs/g3c-mmi-sweep-result-v1.json")
    g3cd = read("runs/g3cd-mmi-targeted-result-v1.json")
    g3c_slot = read("runs/g3c-slot-y-result-v2.json")
    g3c_slot_long = read("runs/g3c-slot-y-result-v3.json")
    g3c_union_y = read("runs/g3c-union-y-result-v1.json")
    g3d = read("runs/g3d-mmi-result-v1.json")
    g3d_eme_width = read("runs/g3d-mmi-eme-width-screen-result-v1.json")
    g4 = read("runs/g4-compact-validation-result-v1.json")
    custom_process = read("configs/custom-process-validation-v1.json")

    length_cm = float(g2["gds_quantized_polyline_um"]) / 10_000.0
    turns = float(g2["turns"])
    equivalent_90 = 4.0 * turns
    bend_loss_per_90_db = -float(bend["meshes"]["25"]["center_transmission_db"])
    composed_bend_loss_db = equivalent_90 * bend_loss_per_90_db
    propagation_db_per_cm = float(baseline["loss_envelope"]["propagation_loss_db_per_cm_assumption"])
    propagation_loss_db = propagation_db_per_cm * length_cm
    delay_path_db = propagation_loss_db + composed_bend_loss_db
    delay_path_db_per_cm = delay_path_db / length_cm
    stress_limit = float(baseline["loss_envelope"]["propagation_plus_bend_limit_db_per_cm"])

    gates = {
        "g1_group_index": "PASS" if g1["g1_passed"] else "FAIL",
        "g2_layout": "PASS" if g2["passed"] else "FAIL",
        "g3a_straight_reference": "PASS",
        "g3b_bend": "PASS" if bend["g3b_bend_passed"] else "FAIL",
        "fabricated_propagation_loss": "OPEN_PDK_OR_CUTBACK",
        "g3c_progressive_tap_and_lo_splitter": "OPEN_REDESIGN" if not (g3c["sweep_passed"] or g3cd["suite_passed"] or g3c_slot["pilot_passed"] or g3c_slot_long["pilot_passed"] or g3c_union_y["pilot_passed"]) else "PASS",
        "g3d_coherent_combiner": "OPEN_REDESIGN" if not g3d_eme_width["screen_passed"] else "OPEN_FDTD_VALIDATION",
        "fast_slot_switch": g4["gates"]["fast_eo_switch_s_parameter_and_bandwidth"],
        "phase_thermal": "OPEN",
        "photodiode_tia": "OPEN",
    }
    return {
        "name": "p6-g5-fail-closed-composition-v1",
        "source_sha256": sha256(Path(__file__)),
        "input_hashes": {
            name: sha256(HERE / path)
            for name, path in {
                "baseline": "configs/baseline-v1.json",
                "g1": "configs/g1-accepted-v1.json",
                "g2": "runs/g2-spiral-layout-result-v1.json",
                "g3b": "runs/g3b-bend-r10-deembedded-fine-convergence-v1.json",
                "g3c": "runs/g3c-mmi-sweep-result-v1.json",
                "g3cd": "runs/g3cd-mmi-targeted-result-v1.json",
                "g3c_slot_y": "runs/g3c-slot-y-result-v2.json",
                "g3c_slot_y_long": "runs/g3c-slot-y-result-v3.json",
                "g3c_union_y": "runs/g3c-union-y-result-v1.json",
                "g3d_mmi": "runs/g3d-mmi-result-v1.json",
                "g3d_eme_width": "runs/g3d-mmi-eme-width-screen-result-v1.json",
                "g4": "runs/g4-compact-validation-result-v1.json",
                "custom_process": "configs/custom-process-validation-v1.json",
            }.items()
        },
        "p5_blind_rerun": False,
        "delay_path": {
            "length_cm": length_cm,
            "equivalent_90deg_bends_from_layout": equivalent_90,
            "fine_fdtd_loss_db_per_90deg": bend_loss_per_90_db,
            "composed_bend_loss_db": composed_bend_loss_db,
            "propagation_loss_db_per_cm_assumption": propagation_db_per_cm,
            "propagation_loss_db_assumption": propagation_loss_db,
            "propagation_plus_bend_db_assumption": delay_path_db,
            "propagation_plus_bend_db_per_cm_assumption": delay_path_db_per_cm,
            "p5_stress_limit_db_per_cm": stress_limit,
            "assumption_within_stress_limit": delay_path_db_per_cm <= stress_limit,
            "physical_evidence_status": "OPEN_UNTIL_PROPAGATION_PDK_OR_CUTBACK",
        },
        "uncomposable_losses": {
            "progressive_tap_excess_and_ratios": "OPEN_G3C",
            "lo_tree_excess": "OPEN_G3C",
            "coherent_combiner_excess": "OPEN_G3D",
            "fast_switch_insertion": "OPEN_G4",
        },
        "gates": gates,
        "g5_composition_complete": all(value == "PASS" for value in gates.values()),
        "p6_accepted": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_g5_record(), indent=2, ensure_ascii=False))
