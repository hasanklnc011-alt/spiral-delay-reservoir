"""Local even/odd supermode synthesis for progressive taps and LO/combiner cells."""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from typing import Any
import numpy as np
import tidy3d as td
from tidy3d.plugins.mode import ModeSolver
from g3_straight_preflight import G1_CONFIG,HERE,REQUIRED_TIDY3D_VERSION
from g3_straight_preflight_v2 import lossless_materials

GAPS_UM=(.15,.20,.25,.30);WAVELENGTH_UM=1.55
def solver(gap:float,mesh:float,parity:int)->ModeSolver:
    a=json.loads(G1_CONFIG.read_text(encoding="utf-8"));w,h=float(a["width_um"]),float(a["height_um"]);pitch=w+gap;si,sio2,_=lossless_materials();cores=tuple(td.Structure(geometry=td.Box(center=(0,y,0),size=(td.inf,w,h)),medium=si,name=f"coupler_{i}") for i,y in enumerate((-pitch/2,pitch/2)));sim=td.Simulation(size=(2,4,3),medium=sio2,structures=cores,sources=(),monitors=(),boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=WAVELENGTH_UM,min_steps_per_wvl=mesh),run_time=1e-12,symmetry=(0,parity,0));return ModeSolver(simulation=sim,plane=td.Box(center=(0,0,0),size=(0,3,2)),mode_spec=td.ModeSpec(num_modes=2,target_neff=1.9,precision="double",sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=.8,filter_order="over",keep_modes=1)),freqs=[td.C_0/WAVELENGTH_UM])
def evaluate()->dict[str,Any]:
    if str(td.__version__)!=REQUIRED_TIDY3D_VERSION:raise RuntimeError("Tidy3D version mismatch")
    cases=[]
    for mesh in (20.0,25.0):
        for gap in GAPS_UM:
            n=[float(np.asarray(solver(gap,mesh,p).solve().n_eff).real.squeeze()) for p in (1,-1)];dn=abs(n[0]-n[1]);kappa=math.pi*dn/WAVELENGTH_UM;l50=WAVELENGTH_UM/(4*dn);cases.append({"mesh":mesh,"gap_um":gap,"even_odd_neff":n,"delta_neff":dn,"kappa_rad_per_um":kappa,"length_50_50_um":l50,"length_full_transfer_um":2*l50})
    selected=[x for x in cases if x["gap_um"]==.2];fine=next(x for x in selected if x["mesh"]==25);coarse=next(x for x in selected if x["mesh"]==20);targets=[]
    for remaining in range(20,0,-1):
        power=1/remaining;targets.append({"remaining_outputs":remaining,"target_power_coupling":power,"interaction_length_um":math.asin(math.sqrt(power))/fine["kappa_rad_per_um"]})
    return {"name":"p6-g3c-directional-coupler-mode-v1","tidy3d_version":str(td.__version__),"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"g1_config_sha256":hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),"cloud_called":False,"cases":cases,"selected_gap_um":.2,"selected_length_50_50_um":fine["length_50_50_um"],"m20_m25_length_relative_delta":abs(coarse["length_50_50_um"]-fine["length_50_50_um"])/fine["length_50_50_um"],"progressive_targets":targets,"compact_s_matrix":"[[cos(kL), -j sin(kL)],[-j sin(kL), cos(kL)]]","passivity":"unitary lossless interaction section; transition excess remains a separate FDTD/PDK gate"}
if __name__=="__main__":print(json.dumps(evaluate(),indent=2))
