"""Cost-gated FDTD isolation of the slot-Y w-to-2w input taper."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d import web
from g3_straight_preflight import G1_CONFIG,HERE
from g3_straight_preflight_v2 import lossless_materials
from g3_straight_cloud import PER_SOURCE_LIMIT_FC,TOTAL_LIMIT_FC
from g3_slot_y_splitter import poly
RUNS=HERE/"runs";ESTIMATE=RUNS/"g3c-slot-y-taper-estimate-v1.json";TAPER_UM=20.;LEAD_UM=4.
def build(mesh:float=15.,run_time_s:float=3e-12)->td.Simulation:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);si,sio2,_=lossless_materials();x0=-TAPER_UM/2;x1=TAPER_UM/2;structures=(td.Structure(geometry=td.Box(center=(x0-LEAD_UM/2,0,0),size=(LEAD_UM,w,h)),medium=si,name="input_lead"),td.Structure(geometry=poly([(x0,-w/2),(x0,w/2),(x1,w),(x1,-w)],h),medium=si,name="w_to_2w_taper"),td.Structure(geometry=td.Box(center=(x1+LEAD_UM/2,0,0),size=(LEAD_UM,2*w,h)),medium=si,name="double_width_lead"));wls=np.linspace(1.52,1.58,13);freqs=td.C_0/wls;f0=td.C_0/1.55;fw=1.5*(max(freqs)-min(freqs));fund=td.ModeSpec(num_modes=2,target_neff=1.87,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1));wide=td.ModeSpec(num_modes=5,target_neff=2.0,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.7,filter_order="over",keep_modes=3));sx=x0-LEAD_UM+1;ix=sx+.75;ox=x1+LEAD_UM-1;source=td.ModeSource(center=(sx,0,0),size=(0,2,1.2),source_time=td.GaussianPulse(freq0=f0,fwidth=fw),direction="+",mode_spec=fund,mode_index=0,name="source");mons=(td.ModeMonitor(center=(ix,0,0),size=(0,2,1.2),freqs=freqs,mode_spec=fund,name="input"),td.ModeMonitor(center=(ox,0,0),size=(0,2,1.2),freqs=freqs,mode_spec=wide,name="output"));return td.Simulation(center=(0,0,0),size=(TAPER_UM+2*LEAD_UM+4,4,2),medium=sio2,structures=structures,sources=(source,),monitors=mons,boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=run_time_s,shutoff=1e-7,subpixel=True,symmetry=(0,0,1))
def metrics(data):
    inc=np.asarray(data["input"].amps.sel(direction="+",mode_index=0));r=np.asarray(data["input"].amps.sel(direction="-",mode_index=0))/inc;amps=np.asarray(data["output"].amps.sel(direction="+"))/inc[:,None];p=np.sum(np.abs(amps)**2,axis=1);res=1-p-np.abs(r)**2;i=6;return {"center_guided_output_power":float(p[i]),"center_excess_loss_db":float(-10*np.log10(max(p[i],1e-30))),"center_reflection_db":float(20*np.log10(max(abs(r[i]),1e-15))),"worst_reflection_db":float(np.max(20*np.log10(np.maximum(abs(r),1e-15)))),"max_abs_energy_residual":float(np.max(np.abs(res)))}
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest();n="p6_g3c_slot_y_taper_only_m15";j=web.Job(simulation=s,task_name=n,folder_name="P6 Physical Validation",verbose=False);j.upload();c=float(j.estimate_cost(verbose=False));return {"name":"p6-g3c-slot-y-taper-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_name":n,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"estimated_flexcredits":c,"solve_started":False,"within_limits":c<PER_SOURCE_LIMIT_FC and c<TOTAL_LIMIT_FC}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    x=json.loads(ESTIMATE.read_text(encoding="utf-8"));s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest()
    if not x["within_limits"] or x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
    p=RUNS/"g3c-slot-y-taper-only_m15-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);data=j.run(path=p);m=metrics(data);ds=re.findall(r"field decay:\s*([0-9.eE+-]+)",str(data.log));decay=float(ds[-1]) if ds else None;passed=m["center_excess_loss_db"]<=.05 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01 and decay is not None and decay<=1e-7;return {"name":"p6-g3c-slot-y-taper-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"final_decay":decay,"metrics":m,"taper_passed":passed,"diagnostic_interpretation":"if taper passes, residual slot-Y reflection is assigned to the slot-tip/interface"}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
