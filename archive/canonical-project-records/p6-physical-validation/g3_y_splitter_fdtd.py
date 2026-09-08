"""Cost-gated symmetric adiabatic Y-splitter candidate for G3-C2."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d import web
from shapely.geometry import LineString
from g3_straight_preflight import G1_CONFIG,HERE
from g3_straight_preflight_v2 import lossless_materials
from g3_straight_cloud import PER_SOURCE_LIMIT_FC,TOTAL_LIMIT_FC

RUNS=HERE/"runs";ESTIMATE_RECORD=RUNS/"g3c-y-splitter-estimate-v1.json"
def polygon(points,width,height):
    p=LineString(points).buffer(width/2,cap_style=2,join_style=2,resolution=24)
    return td.PolySlab(vertices=list(p.exterior.coords)[:-1],slab_bounds=(-height/2,height/2),axis=2)
def build(mesh:float=15.0,transition_um:float=20.0,output_separation_um:float=3.0,run_time_s:float=3e-12)->td.Simulation:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);lead=4.0;x0=-transition_um/2;x1=transition_um/2;xs=np.linspace(x0,x1,301);u=(xs-x0)/transition_um;smooth=.5-.5*np.cos(np.pi*u);yt=output_separation_um/2*smooth;top=[(x0-lead,0)]+list(zip(xs,yt))+[(x1+lead,output_separation_um/2)];bottom=[(x,-y) for x,y in top];si,sio2,_=lossless_materials();structures=(td.Structure(geometry=polygon(top,w,h),medium=si,name="upper_branch"),td.Structure(geometry=polygon(bottom,w,h),medium=si,name="lower_branch"));wls=np.linspace(1.52,1.58,13);freqs=td.C_0/wls;f0=td.C_0/1.55;fw=1.5*(max(freqs)-min(freqs));mode=td.ModeSpec(num_modes=2,target_neff=1.87,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1));source_x=x0-lead+1;input_x=x0-lead+1.75;output_x=x1+lead-1.0;source=td.ModeSource(center=(source_x,0,0),size=(0,2,1.2),source_time=td.GaussianPulse(freq0=f0,fwidth=fw),direction="+",mode_spec=mode,mode_index=0,name="input_source");mons=(td.ModeMonitor(center=(input_x,0,0),size=(0,2,1.2),freqs=freqs,mode_spec=mode,name="input_port"),td.ModeMonitor(center=(output_x,output_separation_um/2,0),size=(0,2,1.2),freqs=freqs,mode_spec=mode,name="output_upper"),td.ModeMonitor(center=(output_x,-output_separation_um/2,0),size=(0,2,1.2),freqs=freqs,mode_spec=mode,name="output_lower"));return td.Simulation(center=(0,0,0),size=(transition_um+2*lead+4,2*output_separation_um+3,2),medium=sio2,structures=structures,sources=(source,),monitors=mons,boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=run_time_s,shutoff=1e-7,subpixel=True,symmetry=(0,0,1))
def metrics(data):
    inc=np.asarray(data["input_port"].amps.sel(direction="+",mode_index=0));r=np.asarray(data["input_port"].amps.sel(direction="-",mode_index=0))/inc;a=np.asarray(data["output_upper"].amps.sel(direction="+",mode_index=0))/inc;b=np.asarray(data["output_lower"].amps.sel(direction="+",mode_index=0))/inc;pa,pb=np.abs(a)**2,np.abs(b)**2;total=pa+pb;res=1-total-np.abs(r)**2;i=6;return {"center_upper_power":float(pa[i]),"center_lower_power":float(pb[i]),"center_total_output_power":float(total[i]),"center_excess_loss_db":float(-10*np.log10(total[i])),"center_imbalance_db":float(abs(10*np.log10(pa[i]/pb[i]))),"center_phase_mismatch_deg":float(abs(np.angle(a[i]/b[i],deg=True))),"center_reflection_db":float(20*np.log10(max(abs(r[i]),1e-15))),"worst_reflection_db":float(np.max(20*np.log10(np.maximum(abs(r),1e-15)))),"max_abs_energy_residual":float(np.max(np.abs(res)))}
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest();n="p6_g3c_y_splitter_m15";j=web.Job(simulation=s,task_name=n,folder_name="P6 Physical Validation",verbose=False);j.upload();c=float(j.estimate_cost(verbose=False));return {"name":"p6-g3c-y-splitter-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_name":n,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"simulation_cells":int(s.num_cells),"computational_grid_points":int(s.num_computational_grid_points),"estimated_flexcredits":c,"solve_started":False,"within_limits":c<PER_SOURCE_LIMIT_FC and c<TOTAL_LIMIT_FC}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    x=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"));s=build();d=hashlib.sha256(s.model_dump_json().encode()).hexdigest()
    if not x["within_limits"] or x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
    p=RUNS/"g3c-y-splitter_m15-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);m=metrics(j.run(path=p));passed=m["center_excess_loss_db"]<=.2 and m["center_imbalance_db"]<=.5 and m["center_phase_mismatch_deg"]<=2 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01;return {"name":"p6-g3c-y-splitter-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"metrics":m,"pilot_passed":passed}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
