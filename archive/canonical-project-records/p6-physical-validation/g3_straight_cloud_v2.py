"""Cost-gated lossless-equivalent G3-A convergence suite."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
import numpy as np
from tidy3d import web
from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC, _sparams
from g3_straight_preflight import HERE
from g3_straight_preflight_v2 import build_straight_v2

RUNS=HERE/"runs"; ESTIMATE_RECORD=RUNS/"g3a-straight-lossless-estimate-v2.json"

def cases()->list[dict[str,float]]: return [{"name":f"length{int(l)}_m{int(m)}","length_um":l,"mesh":m} for m in (20.0,25.0) for l in (4.0,8.0)]
def build_case(case:dict[str,float])->tuple[Any,str]:
    simulation=build_straight_v2(case["length_um"],case["mesh"]); return simulation,hashlib.sha256(simulation.model_dump_json().encode()).hexdigest()

def estimate(*,approved:bool)->dict[str,Any]:
    if not approved: raise PermissionError("User credit approval required")
    jobs=[]
    for case in cases():
        simulation,digest=build_case(case); task_name=f"p6_g3a_lossless_{case['name']}"; job=web.Job(simulation=simulation,task_name=task_name,folder_name="P6 Physical Validation",verbose=False); job.upload(); jobs.append({**case,"task_name":task_name,"task_id":str(job.task_id),"task_status":str(job.get_info().status),"serialized_simulation_sha256":digest,"estimated_flexcredits":float(job.estimate_cost(verbose=False)),"solve_started":False})
    total=sum(x["estimated_flexcredits"] for x in jobs); return {"name":"p6-g3a-straight-lossless-estimate-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"jobs":jobs,"estimated_total_flexcredits":total,"within_limits":total<TOTAL_LIMIT_FC and all(x["estimated_flexcredits"]<PER_SOURCE_LIMIT_FC for x in jobs)}

def execute(*,approved:bool)->dict[str,Any]:
    if not approved: raise PermissionError("User solve approval required")
    record=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not record["within_limits"]: raise RuntimeError("G3-A v2 exceeds limits")
    locked={x["name"]:x for x in record["jobs"]}; results=[]
    for case in cases():
        item=locked[case["name"]]; simulation,digest=build_case(case)
        if digest!=item["serialized_simulation_sha256"] or item["solve_started"]: raise RuntimeError(f"Locked mismatch: {case['name']}")
        path=RUNS/f"g3a-lossless-{case['name']}-result-v2.hdf5"; job=web.Job(simulation=simulation,task_name=item["task_name"],folder_name="P6 Physical Validation",task_id_cached=item["task_id"],verbose=False); data=job.run(path=path); metrics=_sparams(data); results.append({**case,"task_id":item["task_id"],"task_status":str(job.get_info().status),"result_file":path.name,"result_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"actual_flexcredits":float(job.real_cost(verbose=False)),"metrics":metrics})
    by={x["name"]:x for x in results}; conv={}; center=6
    for length in (4,8):
        a=by[f"length{length}_m20"]["metrics"]; b=by[f"length{length}_m25"]["metrics"]; ta=complex(**a["s21"][center]); tb=complex(**b["s21"][center]); conv[str(length)]={"insertion_loss_delta_db":abs(a["transmission_db"][center]-b["transmission_db"][center]),"phase_delta_deg":float(abs(np.angle(ta/tb,deg=True))),"fine_max_abs_energy_residual":b["max_abs_energy_residual"],"fine_worst_reflection_db":b["worst_reflection_db"]}; conv[str(length)]["passed"]=conv[str(length)]["insertion_loss_delta_db"]<0.02 and conv[str(length)]["phase_delta_deg"]<0.5 and b["max_abs_energy_residual"]<0.01 and b["worst_reflection_db"]<-30
    return {"name":"p6-g3a-straight-lossless-result-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"material_policy":"lossless scattering reference; fabricated propagation loss external","results":results,"convergence":conv,"g3a_passed":all(x["passed"] for x in conv.values()),"actual_total_flexcredits":sum(x["actual_flexcredits"] for x in results)}

def main()->None:
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument("--upload-estimates",action="store_true"); g.add_argument("--execute",action="store_true"); p.add_argument("--user-credit-approval",action="store_true"); p.add_argument("--user-solve-approval",action="store_true"); a=p.parse_args(); print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimates else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__": main()
