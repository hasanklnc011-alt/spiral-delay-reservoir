"""Cost-gated long union-branch Y splitter without a width-doubling taper."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d import web
from shapely.geometry import LineString
from g3_straight_preflight import G1_CONFIG,HERE
from g3_straight_preflight_v2 import lossless_materials
from g3_straight_cloud import PER_SOURCE_LIMIT_FC,TOTAL_LIMIT_FC
RUNS=HERE/"runs";ESTIMATE=RUNS/"g3c-union-y-estimate-v1.json";TRANSITION_UM=80.;OUTPUT_CENTER_UM=1.;LEAD_UM=4.
def path_poly(points,w,h):return td.PolySlab(vertices=list(LineString(points).buffer(w/2,cap_style=2,join_style=2,resolution=32).exterior.coords)[:-1],slab_bounds=(-h/2,h/2),axis=2)
def build(mesh:float=15.,run_time_s:float=6e-12)->td.Simulation:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);si,sio2,_=lossless_materials();x0=-TRANSITION_UM/2;x1=TRANSITION_UM/2;xs=np.linspace(x0,x1,801);u=(xs-x0)/TRANSITION_UM;s=.5-.5*np.cos(np.pi*u);y=OUTPUT_CENTER_UM*s;upper=[(x0-LEAD_UM,0.)]+list(zip(xs,y))+[(x1+LEAD_UM,OUTPUT_CENTER_UM)];structures=(td.Structure(geometry=path_poly(upper,w,h),medium=si,name="upper_union_branch"),td.Structure(geometry=path_poly([(x,-yy) for x,yy in upper],w,h),medium=si,name="lower_union_branch"));wls=np.linspace(1.52,1.58,13);freqs=td.C_0/wls;f0=td.C_0/1.55;fw=1.5*(max(freqs)-min(freqs));mode=td.ModeSpec(num_modes=2,target_neff=1.87,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1));sx=x0-LEAD_UM+1;ix=sx+.75;ox=x1+LEAD_UM-1;source=td.ModeSource(center=(sx,0,0),size=(0,2,1.2),source_time=td.GaussianPulse(freq0=f0,fwidth=fw),direction="+",mode_spec=mode,mode_index=0,name="source");mons=(td.ModeMonitor(center=(ix,0,0),size=(0,2,1.2),freqs=freqs,mode_spec=mode,name="input"),td.ModeMonitor(center=(ox,OUTPUT_CENTER_UM,0),size=(0,.65,1.2),freqs=freqs,mode_spec=mode,name="upper"));return td.Simulation(center=(0,0,0),size=(TRANSITION_UM+2*LEAD_UM+4,6,2),medium=sio2,structures=structures,sources=(source,),monitors=mons,boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=run_time_s,shutoff=1e-7,subpixel=True,symmetry=(0,-1,1))
def metrics(data):
    inc=np.asarray(data["input"].amps.sel(direction="+",mode_index=0));r=np.asarray(data["input"].amps.sel(direction="-",mode_index=0))/inc;a=np.asarray(data["upper"].amps.sel(direction="+",mode_index=0))/inc;pa=np.abs(a)**2;total=2*pa;res=1-total-np.abs(r)**2;i=6;return {"center_single_output_power":float(pa[i]),"center_total_output_power_inferred_by_symmetry":float(total[i]),"center_excess_loss_db":float(-10*np.log10(max(total[i],1e-30))),"center_reflection_db":float(20*np.log10(max(abs(r[i]),1e-15))),"worst_reflection_db":float(np.max(20*np.log10(np.maximum(abs(r),1e-15)))),"max_abs_energy_residual":float(np.max(np.abs(res)))}
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest();n="p6_g3c_union_y_long_m15";j=web.Job(simulation=s,task_name=n,folder_name="P6 Physical Validation",verbose=False);j.upload();c=float(j.estimate_cost(verbose=False));return {"name":"p6-g3c-union-y-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_name":n,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"geometry":{"transition_um":TRANSITION_UM,"output_center_um":OUTPUT_CENTER_UM,"width_doubling_taper":False,"y_symmetry":-1},"simulation_cells":int(s.num_cells),"computational_grid_points":int(s.num_computational_grid_points),"estimated_flexcredits":c,"solve_started":False,"within_limits":c<PER_SOURCE_LIMIT_FC and c<TOTAL_LIMIT_FC}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    x=json.loads(ESTIMATE.read_text(encoding="utf-8"));s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest()
    if not x["within_limits"] or x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
    p=RUNS/"g3c-union-y-long_m15-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);data=j.run(path=p);m=metrics(data);ds=re.findall(r"field decay:\s*([0-9.eE+-]+)",str(data.log));decay=float(ds[-1]) if ds else None;passed=m["center_excess_loss_db"]<=.2 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01 and decay is not None and decay<=1e-7;return {"name":"p6-g3c-union-y-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"final_decay":decay,"metrics":m,"nominal_balance_enforced_by_symmetry":True,"fabrication_imbalance_status":"OPEN_UNTIL_NOMINAL_PASSES","pilot_passed":passed}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
