"""Cost-gated m20 convergence check for the selected R=10 um bend."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d import web
from g3_bend_preflight import HERE, build_bend
from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC, _sparams

RUNS=HERE/"runs"; ESTIMATE_RECORD=RUNS/"g3b-bend-r10-m20-estimate-v2.json"
PILOT_FILE=RUNS/"g3b-bend-r10-dense_m15-result-v3.hdf5"
def build_case()->tuple[Any,str]:
    s=build_bend(radius_um=10.0,mesh=20.0,arc_points=385,run_time_s=2.5e-12);return s,hashlib.sha256(s.model_dump_json().encode()).hexdigest()
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    s,d=build_case();name="p6_g3b_bend_r10_dense_m20_rt2p5";j=web.Job(simulation=s,task_name=name,folder_name="P6 Physical Validation",verbose=False);j.upload();c=float(j.estimate_cost(verbose=False));return {"name":"p6-g3b-bend-r10-m20-estimate-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_name":name,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"estimated_flexcredits":c,"solve_started":False,"within_limits":c<PER_SOURCE_LIMIT_FC and c<TOTAL_LIMIT_FC}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    x=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"));s,d=build_case()
    if not x["within_limits"] or x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("Locked G3-B convergence task is not eligible")
    p=RUNS/"g3b-bend-r10-dense_m20-result-v2.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);fine=_sparams(j.run(path=p));coarse=_sparams(td.SimulationData.from_file(PILOT_FILE));center=6;ta=complex(**coarse["s21"][center]);tb=complex(**fine["s21"][center]);conv={"insertion_loss_delta_db":abs(coarse["transmission_db"][center]-fine["transmission_db"][center]),"phase_delta_deg":float(abs(np.angle(ta/tb,deg=True))),"fine_max_abs_energy_residual":fine["max_abs_energy_residual"],"fine_worst_reflection_db":fine["worst_reflection_db"]};conv["passed"]=conv["insertion_loss_delta_db"]<0.02 and conv["phase_delta_deg"]<0.5 and conv["fine_max_abs_energy_residual"]<0.01 and conv["fine_worst_reflection_db"]<-30
    return {"name":"p6-g3b-bend-r10-convergence-result-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False)),"convergence":conv,"g3b_passed":conv["passed"]}
def main()->None:
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
