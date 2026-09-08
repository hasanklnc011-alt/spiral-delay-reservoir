"""Corrected cost-gated slot-opening Y splitter; symmetric slot boundaries."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d import web
from g3_straight_preflight import G1_CONFIG,HERE
from g3_straight_preflight_v2 import lossless_materials
from g3_straight_cloud import PER_SOURCE_LIMIT_FC,TOTAL_LIMIT_FC
from g3_y_splitter_fdtd import metrics
from g3_slot_y_splitter import poly,TAPER_UM,SLOT_OPEN_UM,OUTPUT_CENTER_UM,LEAD_UM

RUNS=HERE/"runs";ESTIMATE=RUNS/"g3c-slot-y-estimate-v2.json"
def build(mesh:float=15.0,run_time_s:float=5e-12)->td.Simulation:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);si,sio2,_=lossless_materials();x0=-(TAPER_UM+SLOT_OPEN_UM)/2;x_t=x0+TAPER_UM;x1=x_t+SLOT_OPEN_UM;final_gap=2*OUTPUT_CENTER_UM-w
    taper=[(x0,-w/2),(x0,w/2),(x_t,w),(x_t,-w)];xs=np.linspace(x_t,x1,401);u=(xs-x_t)/SLOT_OPEN_UM;s=.5-.5*np.cos(np.pi*u);g=final_gap*s;outer=w+g/2
    outer_vertices=list(zip(xs,-outer))+list(zip(xs[::-1],outer[::-1]));slot_vertices=[(x_t,0.0)]+list(zip(xs[1:],-g[1:]/2))+list(zip(xs[:0:-1],g[:0:-1]/2))
    structures=[td.Structure(geometry=td.Box(center=(x0-LEAD_UM/2,0,0),size=(LEAD_UM,w,h)),medium=si,name="input_lead"),td.Structure(geometry=poly(taper,h),medium=si,name="input_double_width_taper"),td.Structure(geometry=poly(outer_vertices,h),medium=si,name="outer_silicon"),td.Structure(geometry=poly(slot_vertices,h),medium=sio2,name="symmetric_opening_silica_slot")]
    for sign,name in ((1,"upper"),(-1,"lower")):structures.append(td.Structure(geometry=td.Box(center=(x1+LEAD_UM/2,sign*OUTPUT_CENTER_UM,0),size=(LEAD_UM,w,h)),medium=si,name=f"{name}_lead"))
    wls=np.linspace(1.52,1.58,13);freqs=td.C_0/wls;f0=td.C_0/1.55;fw=1.5*(max(freqs)-min(freqs));mode=td.ModeSpec(num_modes=2,target_neff=1.87,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1));sx=x0-LEAD_UM+1;ix=sx+.75;ox=x1+LEAD_UM-1;source=td.ModeSource(center=(sx,0,0),size=(0,2,1.2),source_time=td.GaussianPulse(freq0=f0,fwidth=fw),direction="+",mode_spec=mode,mode_index=0,name="input_source");mons=(td.ModeMonitor(center=(ix,0,0),size=(0,2,1.2),freqs=freqs,mode_spec=mode,name="input_port"),td.ModeMonitor(center=(ox,OUTPUT_CENTER_UM,0),size=(0,.65,1.2),freqs=freqs,mode_spec=mode,name="output_upper"),td.ModeMonitor(center=(ox,-OUTPUT_CENTER_UM,0),size=(0,.65,1.2),freqs=freqs,mode_spec=mode,name="output_lower"));return td.Simulation(center=(0,0,0),size=(TAPER_UM+SLOT_OPEN_UM+2*LEAD_UM+4,6,2),medium=sio2,structures=tuple(structures),sources=(source,),monitors=mons,boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=run_time_s,shutoff=1e-7,subpixel=True,symmetry=(0,0,1))
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest();n="p6_g3c_slot_y_v2_m15";j=web.Job(simulation=s,task_name=n,folder_name="P6 Physical Validation",verbose=False);j.upload();c=float(j.estimate_cost(verbose=False));return {"name":"p6-g3c-slot-y-estimate-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_name":n,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"simulation_cells":int(s.num_cells),"computational_grid_points":int(s.num_computational_grid_points),"run_time_s":s.run_time,"estimated_flexcredits":c,"solve_started":False,"within_limits":c<PER_SOURCE_LIMIT_FC and c<TOTAL_LIMIT_FC}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    x=json.loads(ESTIMATE.read_text(encoding="utf-8"));s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest()
    if not x["within_limits"] or x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
    p=RUNS/"g3c-slot-y-v2_m15-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);data=j.run(path=p);m=metrics(data);decay=float(data.log.final_decay_value);passed=m["center_excess_loss_db"]<=.2 and m["center_imbalance_db"]<=.5 and m["center_phase_mismatch_deg"]<=2 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01 and decay<=1e-7;return {"name":"p6-g3c-slot-y-result-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"geometry":{"input_taper_um":TAPER_UM,"slot_open_um":SLOT_OPEN_UM,"output_center_um":OUTPUT_CENTER_UM,"slot_boundary_fix":"both boundaries use +/-g/2"},"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"final_decay":decay,"metrics":m,"symmetry_invariant_passed":m["center_imbalance_db"]<.01,"evidence_valid":m["center_imbalance_db"]<.01,"pilot_passed":passed}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
