"""Local supermode coupling bounds for adjacent spiral turns."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver
from g3_straight_preflight import G1_CONFIG,HERE,REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials

PITCHES_UM=(3.0,4.0,5.0,6.0);MAX_PARALLEL_LENGTH_UM=2991.859094053419
def solver(pitch:float,mesh:float,parity:int)->ModeSolver:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);si,sio2,_=lossless_materials();cores=tuple(td.Structure(geometry=td.Box(center=(0,y,0),size=(td.inf,w,h)),medium=si,name=f"turn_{i}") for i,y in enumerate((-pitch/2,pitch/2)))
    sim=td.Simulation(size=(2,2*pitch+3,3),medium=sio2,structures=cores,sources=(),monitors=(),boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=1e-12,symmetry=(0,parity,0))
    return ModeSolver(simulation=sim,plane=td.Box(center=(0,0,0),size=(0,2*pitch+2,2)),mode_spec=td.ModeSpec(num_modes=2,target_neff=1.87,precision="double",sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1)),freqs=[td.C_0/1.55])
def evaluate()->dict[str,Any]:
    if str(td.__version__)!=REQUIRED_TIDY3D_VERSION:raise RuntimeError("Tidy3D version mismatch")
    cases=[]
    for mesh in (20.0,25.0):
        for pitch in PITCHES_UM:
            neff=[float(np.asarray(solver(pitch,mesh,p).solve().n_eff).real.squeeze()) for p in (1,-1)];split=float(abs(neff[0]-neff[1]));kappa=np.pi*split/1.55;xtalk=float(np.sin(kappa*MAX_PARALLEL_LENGTH_UM)**2);cases.append({"mesh":mesh,"pitch_um":pitch,"edge_gap_um":pitch-.343,"even_odd_te_neff":neff,"delta_neff":split,"coupling_length_um":float(np.pi/(2*kappa)) if kappa>0 else None,"max_segment_crosstalk_power":xtalk,"max_segment_crosstalk_db":float(10*np.log10(max(xtalk,1e-30)))})
    selected=[x for x in cases if x["pitch_um"]==5.0];worst=max(x["max_segment_crosstalk_power"] for x in selected);return {"name":"p6-g3b-adjacent-turn-supermode-v2","tidy3d_version":str(td.__version__),"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"g1_config_sha256":hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),"cloud_called":False,"parallel_length_assumption_um":MAX_PARALLEL_LENGTH_UM,"assumption":"conservative ceiling for one outer spiral turn; replace with exact GDS segment inventory","cases":cases,"selected_pitch_um":5.0,"selected_worst_crosstalk_db":float(10*np.log10(max(worst,1e-30))),"passed":worst<1e-3}
if __name__=="__main__":print(json.dumps(evaluate(),indent=2))
