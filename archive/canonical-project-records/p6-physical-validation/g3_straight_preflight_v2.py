"""Lossless-equivalent G3-A scattering reference; propagation loss stays external."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import tidy3d as td

from g3_straight_preflight import G1_CONFIG, HERE


def lossless_materials() -> tuple[td.Medium, td.Medium, dict[str, float]]:
    frequency = td.C_0 / 1.55
    silicon_model = td.material_library["cSi"]["Li1993_293K"]
    silica_model = td.material_library["SiO2"]["Horiba"]
    silicon_eps = float(np.real(silicon_model.eps_model(frequency)))
    silica_eps = float(np.real(silica_model.eps_model(frequency)))
    return td.Medium(permittivity=silicon_eps), td.Medium(permittivity=silica_eps), {"silicon_permittivity": silicon_eps, "silica_permittivity": silica_eps}


def build_straight_v2(length_um: float, mesh: float) -> td.Simulation:
    accepted=json.loads(G1_CONFIG.read_text(encoding="utf-8")); width=float(accepted["width_um"]); height=float(accepted["height_um"])
    wavelengths=np.linspace(1.52,1.58,13); freqs=td.C_0/wavelengths; freq0=td.C_0/1.55; fwidth=1.5*(max(freqs)-min(freqs))
    source_x=-length_um/2-0.75; input_x=-length_um/2; output_x=length_um/2
    mode_spec=td.ModeSpec(num_modes=3,target_neff=1.9,sort_spec=td.ModeSortSpec(filter_key="TE_fraction",filter_reference=0.8,filter_order="over",keep_modes=1)); port_size=(0.0,2.0,1.5)
    silicon,silica,_=lossless_materials(); structure=td.Structure(geometry=td.Box(center=(0,0,0),size=(td.inf,width,height)),medium=silicon,name="lossless_scattering_strip")
    source=td.ModeSource(center=(source_x,0,0),size=port_size,source_time=td.GaussianPulse(freq0=freq0,fwidth=fwidth),direction="+",mode_spec=mode_spec,mode_index=0,name="te0_source")
    monitors=(td.ModeMonitor(center=(input_x,0,0),size=port_size,freqs=freqs,mode_spec=mode_spec,name="input_port"),td.ModeMonitor(center=(output_x,0,0),size=port_size,freqs=freqs,mode_spec=mode_spec,name="output_port"),td.FluxMonitor(center=(input_x,0,0),size=port_size,freqs=freqs,name="input_flux"),td.FluxMonitor(center=(output_x,0,0),size=port_size,freqs=freqs,name="output_flux"))
    return td.Simulation(center=(0,0,0),size=(length_um+4,3,2.5),medium=silica,structures=(structure,),sources=(source,),monitors=monitors,boundary_spec=td.BoundarySpec.all_sides(boundary=td.PML()),grid_spec=td.GridSpec.auto(wavelength=1.55,min_steps_per_wvl=mesh),run_time=2e-12,shutoff=1e-7,subpixel=True)


def preflight()->dict[str,Any]:
    cases=[]
    for mesh in (20.0,25.0):
        for length in (4.0,8.0):
            simulation=build_straight_v2(length,mesh); serialized=simulation.model_dump_json(); cases.append({"name":f"length{int(length)}_m{int(mesh)}","length_um":length,"mesh":mesh,"cells":int(simulation.num_cells),"serialized_sha256":hashlib.sha256(serialized.encode()).hexdigest()})
    _,_,materials=lossless_materials()
    return {"name":"p6-g3a-lossless-preflight-v2","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"g1_config_sha256":hashlib.sha256(G1_CONFIG.read_bytes()).hexdigest(),"material_policy":"lossless equivalent for component scattering; propagation loss external from PDK/cutback","materials":materials,"cloud_called":False,"cases":cases,"passed":True}


if __name__=="__main__": print(json.dumps(preflight(),indent=2))
