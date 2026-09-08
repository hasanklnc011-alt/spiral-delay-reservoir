"""Cost-gated 3D FDTD length sweep for a symmetric 1x2 MMI splitter."""
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
RUNS=HERE/"runs";ESTIMATE_RECORD=RUNS/"g3c-mmi-sweep-estimate-v1.json";LENGTHS=(4.,6.,8.,10.,12.)
def slab(vertices,h):return td.PolySlab(vertices=vertices,slab_bounds=(-h/2,h/2),axis=2)
def build(length:float,mesh:float=15.)->td.Simulation:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);si,sio2,_=lossless_materials();wmmi=2.;wa=.6;y=.55;taper=1.5;lead=3.;xl=-length/2;xr=length/2;structures=[td.Structure(geometry=td.Box(center=((xl-taper-lead/2),0,0),size=(lead,w,h)),medium=si,name="input_lead"),td.Structure(geometry=slab([(xl-taper,-w/2),(xl-taper,w/2),(xl,wa/2),(xl,-wa/2)],h),medium=si,name="input_taper"),td.Structure(geometry=td.Box(center=(0,0,0),size=(length,wmmi,h)),medium=si,name="mmi")]
    for sign,name in ((1,"upper"),(-1,"lower")):
        yc=sign*y;structures.extend([td.Structure(geometry=slab([(xr,yc-wa/2),(xr,yc+wa/2),(xr+taper,yc+w/2),(xr+taper,yc-w/2)],h),medium=si,name=f"{name}_taper"),td.Structure(geometry=td.Box(center=(xr+taper+lead/2,yc,0),size=(lead,w,h)),medium=si,name=f"{name}_lead")])
    wls=np.linspace(1.52,1.58,13);freqs=td.C_0/wls;f0=td.C_0/1.55;fw=1.5*(max(freqs)-min(freqs));mode=td.ModeSpec(num_modes=2,target_neff=1.87,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1));sx=xl-taper-lead+1;ix=sx+.75;ox=xr+taper+lead-1;source=td.ModeSource(center=(sx,0,0),size=(0,2,1.2),source_time=td.GaussianPulse(freq0=f0,fwidth=fw),direction="+",mode_spec=mode,mode_index=0,name="source");mons=(td.ModeMonitor(center=(ix,0,0),size=(0,2,1.2),freqs=freqs,mode_spec=mode,name="input"),td.ModeMonitor(center=(ox,y,0),size=(0,.75,1.2),freqs=freqs,mode_spec=mode,name="upper"),td.ModeMonitor(center=(ox,-y,0),size=(0,.75,1.2),freqs=freqs,mode_spec=mode,name="lower"));return td.Simulation(center=(0,0,0),size=(length+2*taper+2*lead+4,6,2),medium=sio2,structures=tuple(structures),sources=(source,),monitors=mons,boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=2.5e-12,shutoff=1e-7,subpixel=True,symmetry=(0,0,1))
def metrics(data):
    inc=np.asarray(data["input"].amps.sel(direction="+",mode_index=0));r=np.asarray(data["input"].amps.sel(direction="-",mode_index=0))/inc;a=np.asarray(data["upper"].amps.sel(direction="+",mode_index=0))/inc;b=np.asarray(data["lower"].amps.sel(direction="+",mode_index=0))/inc;pa,pb=np.abs(a)**2,np.abs(b)**2;total=pa+pb;res=1-total-np.abs(r)**2;i=6;return {"center_upper_power":float(pa[i]),"center_lower_power":float(pb[i]),"center_total_output_power":float(total[i]),"center_excess_loss_db":float(-10*np.log10(max(total[i],1e-30))),"center_imbalance_db":float(abs(10*np.log10(max(pa[i],1e-30)/max(pb[i],1e-30)))),"center_phase_mismatch_deg":float(abs(np.angle(a[i]/b[i],deg=True))),"center_reflection_db":float(20*np.log10(max(abs(r[i]),1e-15))),"worst_reflection_db":float(np.max(20*np.log10(np.maximum(abs(r),1e-15)))),"max_abs_energy_residual":float(np.max(np.abs(res)))}
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    jobs=[]
    for length in LENGTHS:
        s=build(length);d=hashlib.sha256(s.model_dump_json().encode()).hexdigest();name=f"p6_g3c_mmi_l{int(length)}_m15";j=web.Job(simulation=s,task_name=name,folder_name="P6 Physical Validation",verbose=False);j.upload();jobs.append({"length_um":length,"task_name":name,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"estimated_flexcredits":float(j.estimate_cost(verbose=False)),"solve_started":False})
    total=sum(x["estimated_flexcredits"] for x in jobs);return {"name":"p6-g3c-mmi-sweep-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"jobs":jobs,"estimated_total_flexcredits":total,"within_limits":total<TOTAL_LIMIT_FC and all(x["estimated_flexcredits"]<PER_SOURCE_LIMIT_FC for x in jobs)}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    rec=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"));locked={float(x["length_um"]):x for x in rec["jobs"]};results=[]
    if not rec["within_limits"]:raise RuntimeError("MMI suite exceeds limits")
    for length in LENGTHS:
        x=locked[length];s=build(length);d=hashlib.sha256(s.model_dump_json().encode()).hexdigest()
        if x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
        p=RUNS/f"g3c-mmi-l{int(length)}_m15-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);m=metrics(j.run(path=p));passed=m["center_excess_loss_db"]<=.2 and m["center_imbalance_db"]<=.5 and m["center_phase_mismatch_deg"]<=2 and m["worst_reflection_db"]<-30 and m["max_abs_energy_residual"]<.01;results.append({"length_um":length,"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False) or 0),"metrics":m,"passed":passed})
    feasible=[x for x in results if x["passed"]];return {"name":"p6-g3c-mmi-sweep-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"results":results,"selected_length_um":min(feasible,key=lambda x:x["metrics"]["center_excess_loss_db"])["length_um"] if feasible else None,"sweep_passed":bool(feasible),"actual_total_flexcredits":sum(x["actual_flexcredits"] for x in results)}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimates",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimates else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
