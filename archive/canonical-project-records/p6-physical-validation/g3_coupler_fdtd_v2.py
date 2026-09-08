"""Redesigned 50:50 coupler pilot with wider isolated ports and calibrated phase."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from tidy3d import web
from g3_coupler_fdtd import HERE,RUNS,build,metrics
from g3_straight_cloud import PER_SOURCE_LIMIT_FC,TOTAL_LIMIT_FC
ESTIMATE_RECORD=RUNS/"g3c-coupler-fdtd-estimate-v2.json"
def sim():return build(mesh=15,interaction_length=1.70,far=3.0,transition=15.0,port_span=2.0,run_time_s=3e-12)
def estimate(*,approved):
    if not approved:raise PermissionError("User credit approval required")
    s=sim();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest();n="p6_g3c_coupler_50_50_wideport_m15";j=web.Job(simulation=s,task_name=n,folder_name="P6 Physical Validation",verbose=False);j.upload();c=float(j.estimate_cost(verbose=False));return {"name":"p6-g3c-coupler-fdtd-estimate-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_name":n,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"simulation_cells":int(s.num_cells),"computational_grid_points":int(s.num_computational_grid_points),"estimated_flexcredits":c,"solve_started":False,"within_limits":c<PER_SOURCE_LIMIT_FC and c<TOTAL_LIMIT_FC}
def execute(*,approved):
    if not approved:raise PermissionError("User solve approval required")
    x=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"));s=sim();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest()
    if not x["within_limits"] or x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
    p=RUNS/"g3c-coupler-50_50-wideport_m15-result-v2.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);m=metrics(j.run(path=p));passed=m["center_excess_loss_db"]<=.2 and m["center_imbalance_db"]<=.5 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01;return {"name":"p6-g3c-coupler-fdtd-result-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"metrics":m,"pilot_passed":passed}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
