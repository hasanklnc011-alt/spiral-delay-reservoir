"""Machine-readable P6 requirement audit; negative/open evidence stays fail-closed."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent
def load(path:str)->dict[str,Any]:return json.loads((HERE/path).read_text(encoding="utf-8"))
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def audit()->dict[str,Any]:
    baseline=load("configs/baseline-v1.json");g1=load("configs/g1-accepted-v1.json");g2=load("runs/g2-spiral-layout-result-v1.json");g3b=load("runs/g3b-bend-r10-deembedded-fine-convergence-v1.json");g3cd=load("runs/g3cd-mmi-targeted-result-v1.json");g3c_slot=load("runs/g3c-slot-y-result-v2.json");g3c_slot_long=load("runs/g3c-slot-y-result-v3.json");g3c_union_y=load("runs/g3c-union-y-result-v1.json");g3d=load("runs/g3d-mmi-result-v1.json");g4=load("runs/g4-compact-validation-result-v1.json");g5=load("runs/g5-composition-result-v1.json")
    requirements={
      "G0_provenance":{"status":"PASS","evidence":"baseline blind/candidate hashes; rerun forbidden"},
      "G1_delay_cross_section":{"status":"PASS" if g1["g1_passed"] else "FAIL","evidence":"configs/g1-accepted-v1.json"},
      "G2_layout":{"status":"PASS" if g2["passed"] else "FAIL","evidence":"runs/g2-spiral-layout-result-v1.json"},
      "G3A_straight_reference":{"status":"PASS","evidence":"G3A-ACCEPTANCE.md"},
      "G3B_bend_and_crosstalk":{"status":"PASS" if g3b["g3b_bend_passed"] else "FAIL","evidence":"G3B-ACCEPTANCE.md"},
      "G3C_splitter_tap":{"status":"FAIL_REDESIGN" if not (g3cd["suite_passed"] or g3c_slot["pilot_passed"] or g3c_slot_long["pilot_passed"] or g3c_union_y["pilot_passed"]) else "PASS","evidence":"G3C-STATUS.md"},
      "G3D_coherent_combiner":{"status":"FAIL_REDESIGN" if not g3d["pilot_passed"] else "PASS","evidence":"G3D-STATUS.md"},
      "G4_fast_switch_phase":{"status":"OPEN","evidence":g4["gates"]["fast_eo_switch_s_parameter_and_bandwidth"]},
      "G4_photodiode_tia":{"status":"OPEN","evidence":g4["gates"]["pd_tia_linearity_at_required_current"]},
      "G4_thermal":{"status":"OPEN","evidence":"assumption-only; PDK/thermal solve missing"},
      "G5_full_link":{"status":"OPEN" if not g5["g5_composition_complete"] else "PASS","evidence":"runs/g5-composition-result-v1.json"},
    }
    return {"name":"p6-g6-physical-acceptance-audit-v1","source_sha256":sha(Path(__file__)),"baseline_sha256":sha(HERE/"configs/baseline-v1.json"),"p5_blind_rerun":False,"requirements":requirements,"passed_count":sum(x["status"]=="PASS" for x in requirements.values()),"total_count":len(requirements),"p6_accepted":all(x["status"]=="PASS" for x in requirements.values()),"verdict":"NOT_PHYSICALLY_ACCEPTED","next_required_evidence":["foundry-qualified or transition-redesigned splitter/tap complex S-matrix","accepted reciprocal 2x2 combiner complex S-matrix","fabricated propagation loss from PDK/cutback","30 GHz fast-switch S-parameters","50 GHz PD/TIA saturation/noise/linearity","phase-shifter and thermal PDK/solve/measurement"]}
if __name__=="__main__":print(json.dumps(audit(),indent=2))
