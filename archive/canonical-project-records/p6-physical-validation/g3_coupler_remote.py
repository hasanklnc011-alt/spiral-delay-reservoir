"""Cost-gated remote/subpixel supermode validation for the selected 200 nm gap."""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d import web
from tidy3d.plugins.mode import ModeSolver,ModeSolverData
from g3_straight_preflight import G1_CONFIG,HERE
from g3_straight_preflight_v2 import lossless_materials
from g3_straight_cloud import PER_SOURCE_LIMIT_FC,TOTAL_LIMIT_FC
RUNS=HERE/"runs";ESTIMATE_RECORD=RUNS/"g3c-coupler-mode-estimate-v1.json";GAP=.2;WL=np.linspace(1.52,1.58,13)
def build(mesh:float)->tuple[ModeSolver,str]:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);pitch=w+GAP;si,sio2,_=lossless_materials();cores=tuple(td.Structure(geometry=td.Box(center=(0,y,0),size=(td.inf,w,h)),medium=si,name=f"coupler_{i}") for i,y in enumerate((-pitch/2,pitch/2)));sim=td.Simulation(size=(2,4,3),medium=sio2,structures=cores,sources=(),monitors=(),boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=1e-12);solver=ModeSolver(simulation=sim,plane=td.Box(center=(0,0,0),size=(0,3,2)),mode_spec=td.ModeSpec(num_modes=4,target_neff=1.9,precision="double",sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=2)),freqs=td.C_0/WL);return solver,hashlib.sha256(solver.model_dump_json().encode()).hexdigest()
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    jobs=[]
    for mesh in (20.,25.):
        s,d=build(mesh);name=f"p6_g3c_coupler_gap200nm_m{int(mesh)}";j=web.Job(simulation=s,task_name=name,folder_name="P6 Physical Validation",verbose=False);j.upload();jobs.append({"mesh":mesh,"task_name":name,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_solver_sha256":d,"estimated_flexcredits":float(j.estimate_cost(verbose=False)),"solve_started":False})
    total=sum(x["estimated_flexcredits"] for x in jobs);return {"name":"p6-g3c-coupler-mode-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"jobs":jobs,"estimated_total_flexcredits":total,"within_limits":total<TOTAL_LIMIT_FC and all(x["estimated_flexcredits"]<PER_SOURCE_LIMIT_FC for x in jobs)}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    rec=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"));locked={float(x["mesh"]):x for x in rec["jobs"]};results=[]
    if not rec["within_limits"]:raise RuntimeError("coupler mode suite exceeds limits")
    for mesh in (20.,25.):
        x=locked[mesh];s,d=build(mesh)
        if x["solve_started"] or d!=x["serialized_solver_sha256"]:raise RuntimeError("locked mismatch")
        p=RUNS/f"g3c-coupler-gap200nm_m{int(mesh)}-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);data=j.run(path=p);ne=np.asarray(data.n_eff).real;dn=np.abs(ne[:,0]-ne[:,1]);length=WL/(4*dn);results.append({"mesh":mesh,"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"delta_neff":[float(v) for v in dn],"length_50_50_um":[float(v) for v in length]})
    a,b=results;rel=abs(a["length_50_50_um"][6]-b["length_50_50_um"][6])/b["length_50_50_um"][6];fine=b;targets=[];kappa=math.pi*fine["delta_neff"][6]/1.55
    for rem in range(20,0,-1):targets.append({"remaining_outputs":rem,"target_power_coupling":1/rem,"interaction_length_um":math.asin(math.sqrt(1/rem))/kappa})
    return {"name":"p6-g3c-coupler-mode-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"results":results,"center_length_relative_mesh_delta":rel,"selected_gap_um":GAP,"fine_length_50_50_um":fine["length_50_50_um"][6],"fine_wavelength_length_variation_fraction":(max(fine["length_50_50_um"])-min(fine["length_50_50_um"]))/fine["length_50_50_um"][6],"progressive_targets":targets,"mode_gate_passed":rel<.01}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimates",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimates else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
