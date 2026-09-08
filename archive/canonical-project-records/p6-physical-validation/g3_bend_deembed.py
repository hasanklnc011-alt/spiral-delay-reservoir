"""De-embed straight propagation phase from the selected bend mesh pair."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import tidy3d as td
from g3_straight_cloud import _sparams
from g3_straight_preflight import HERE

RUNS=HERE/"runs"
FILES={
    15:{"bend":"g3b-bend-r10-dense_m15-result-v3.hdf5","straight4":"g3a-lossless-length4_m15-result-v1.hdf5","straight8":"g3a-lossless-length8_m15-result-v1.hdf5"},
    20:{"bend":"g3b-bend-r10-dense_m20-result-v2.hdf5","straight4":"g3a-lossless-length4_m20-result-v2.hdf5","straight8":"g3a-lossless-length8_m20-result-v2.hdf5"},
}
def load(name):return _sparams(td.SimulationData.from_file(RUNS/name))
def c(values,index):return complex(**values[index])
def evaluate():
    wavelength=1.55;center=6;path_um=2.2+np.pi*10.0/2.0+2.2;expected_beta=2*np.pi*1.87/wavelength;rows={}
    for mesh,names in FILES.items():
        b,s4,s8=load(names["bend"]),load(names["straight4"]),load(names["straight8"]);raw=np.angle(c(s8["s21"],center)/c(s4["s21"],center));cycles=round((expected_beta*4.0-raw)/(2*np.pi));beta=(raw+2*np.pi*cycles)/4.0;excess=np.angle(c(b["s21"],center)*np.exp(-1j*beta*path_um));rows[str(mesh)]={"straight_beta_rad_per_um":float(beta),"equivalent_neff":float(beta*wavelength/(2*np.pi)),"bend_path_um":float(path_um),"deembedded_excess_phase_deg":float(np.degrees(excess)),"center_transmission_db":b["transmission_db"][center],"worst_reflection_db":b["worst_reflection_db"],"max_abs_energy_residual":b["max_abs_energy_residual"]}
    phase_delta=float(abs(np.degrees(np.angle(np.exp(1j*np.radians(rows["15"]["deembedded_excess_phase_deg"]-rows["20"]["deembedded_excess_phase_deg"]))))));il_delta=abs(rows["15"]["center_transmission_db"]-rows["20"]["center_transmission_db"]);passed=phase_delta<0.5 and il_delta<0.02 and rows["20"]["worst_reflection_db"]<-30 and rows["20"]["max_abs_energy_residual"]<0.01
    return {"name":"p6-g3b-bend-r10-deembedded-convergence-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"reference":"two-length lossless G3-A straight phase slope at each mesh","meshes":rows,"convergence":{"insertion_loss_delta_db":il_delta,"deembedded_phase_delta_deg":phase_delta,"passed":passed},"g3b_bend_passed":passed}
if __name__=="__main__":print(json.dumps(evaluate(),indent=2))
