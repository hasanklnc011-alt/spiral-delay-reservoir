"""Final m20/m25 straight-reference de-embedding for the selected bend."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import tidy3d as td
from g3_straight_cloud import _sparams
from g3_straight_preflight import HERE
RUNS=HERE/"runs"
FILES={20:{"bend":"g3b-bend-r10-dense_m20-result-v2.hdf5","straight4":"g3a-lossless-length4_m20-result-v2.hdf5","straight8":"g3a-lossless-length8_m20-result-v2.hdf5"},25:{"bend":"g3b-bend-r10-dense_m25-result-v2.hdf5","straight4":"g3a-lossless-length4_m25-result-v2.hdf5","straight8":"g3a-lossless-length8_m25-result-v2.hdf5"}}
def load(n):return _sparams(td.SimulationData.from_file(RUNS/n))
def z(v,i):return complex(**v[i])
def evaluate():
    wl=1.55;i=6;length=4.4+np.pi*10/2;expected=2*np.pi*1.87/wl;rows={}
    for mesh,f in FILES.items():
        b,a,c=load(f["bend"]),load(f["straight4"]),load(f["straight8"]);raw=np.angle(z(c["s21"],i)/z(a["s21"],i));beta=(raw+2*np.pi*round((expected*4-raw)/(2*np.pi)))/4;phase=np.angle(z(b["s21"],i)*np.exp(-1j*beta*length));rows[str(mesh)]={"straight_beta_rad_per_um":float(beta),"equivalent_neff":float(beta*wl/(2*np.pi)),"deembedded_excess_phase_deg":float(np.degrees(phase)),"center_transmission_db":b["transmission_db"][i],"worst_reflection_db":b["worst_reflection_db"],"max_abs_energy_residual":b["max_abs_energy_residual"]}
    delta=float(abs(np.degrees(np.angle(np.exp(1j*np.radians(rows["20"]["deembedded_excess_phase_deg"]-rows["25"]["deembedded_excess_phase_deg"]))))));il=abs(rows["20"]["center_transmission_db"]-rows["25"]["center_transmission_db"]);passed=delta<0.5 and il<0.02 and rows["25"]["worst_reflection_db"]<-30 and rows["25"]["max_abs_energy_residual"]<0.01
    return {"name":"p6-g3b-bend-r10-deembedded-fine-convergence-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"reference":"m20/m25 two-length G3-A lossless straight phase slope","meshes":rows,"convergence":{"insertion_loss_delta_db":il,"deembedded_phase_delta_deg":delta,"passed":passed},"g3b_bend_passed":passed}
if __name__=="__main__":print(json.dumps(evaluate(),indent=2))
