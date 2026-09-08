"""Post-process the completed slot-Y v2 HDF5 without starting another solve."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
import tidy3d as td
from tidy3d import web
from g3_y_splitter_fdtd import metrics
from g3_slot_y_splitter_v2 import build,RUNS,ESTIMATE,TAPER_UM,SLOT_OPEN_UM,OUTPUT_CENTER_UM
def process():
    x=json.loads(ESTIMATE.read_text(encoding="utf-8"));p=RUNS/"g3c-slot-y-v2_m15-result-v1.hdf5";data=td.SimulationData.from_file(p);m=metrics(data);decays=re.findall(r"field decay:\s*([0-9.eE+-]+)",str(data.log));decay=float(decays[-1]) if decays else None;j=web.Job(simulation=build(),task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);sym=m["center_imbalance_db"]<=.5;passed=m["center_excess_loss_db"]<=.2 and m["center_imbalance_db"]<=.5 and m["center_phase_mismatch_deg"]<=2 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01 and decay is not None and decay<=1e-7;return {"name":"p6-g3c-slot-y-result-v2","postprocessor_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"builder_source_sha256":x["source_sha256"],"estimate_sha256":hashlib.sha256(ESTIMATE.read_bytes()).hexdigest(),"geometry":{"input_taper_um":TAPER_UM,"slot_open_um":SLOT_OPEN_UM,"output_center_um":OUTPUT_CENTER_UM,"slot_boundary_fix":"both boundaries use +/-g/2"},"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"final_decay":decay,"metrics":m,"symmetry_acceptance_limit_db":.5,"symmetry_invariant_passed":sym,"evidence_valid":sym,"pilot_passed":passed,"solve_restarted":False}
if __name__=="__main__":print(json.dumps(process(),indent=2))
