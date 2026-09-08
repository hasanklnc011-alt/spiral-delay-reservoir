"""Cost-gated mesh convergence for the G3-A straight reference."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from tidy3d import web

from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC, _sparams
from g3_straight_preflight import HERE, build_straight


RUNS = HERE / "runs"
ESTIMATE_RECORD = RUNS / "g3a-straight-convergence-estimate-v1.json"


def cases() -> list[dict[str, float]]:
    return [{"name": f"length{int(length)}_m{int(mesh)}", "length_um": length, "mesh": mesh} for mesh in (20.0, 25.0) for length in (4.0, 8.0)]


def build_case(case: dict[str, float]) -> tuple[Any, str]:
    simulation = build_straight(case["length_um"], mesh=case["mesh"])
    return simulation, hashlib.sha256(simulation.model_dump_json().encode("utf-8")).hexdigest()


def estimate(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User credit approval required")
    jobs = []
    for case in cases():
        simulation, digest = build_case(case)
        task_name = f"p6_g3a_straight_{case['name']}"
        job = web.Job(simulation=simulation, task_name=task_name, folder_name="P6 Physical Validation", verbose=False)
        job.upload()
        jobs.append({**case, "task_name":task_name,"task_id":str(job.task_id),"task_status":str(job.get_info().status),"serialized_simulation_sha256":digest,"estimated_flexcredits":float(job.estimate_cost(verbose=False)),"solve_started":False})
    total=sum(item["estimated_flexcredits"] for item in jobs)
    return {"name":"p6-g3a-straight-convergence-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"jobs":jobs,"estimated_total_flexcredits":total,"within_limits":total<TOTAL_LIMIT_FC and all(item["estimated_flexcredits"]<PER_SOURCE_LIMIT_FC for item in jobs)}


def execute(*, approved: bool) -> dict[str, Any]:
    if not approved:
        raise PermissionError("User solve approval required")
    record=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"))
    if not record["within_limits"]:
        raise RuntimeError("G3-A convergence exceeds limits")
    locked={item["name"]:item for item in record["jobs"]}
    results=[]
    for case in cases():
        item=locked[case["name"]]
        simulation,digest=build_case(case)
        if digest!=item["serialized_simulation_sha256"] or item["solve_started"]:
            raise RuntimeError(f"Locked case mismatch: {case['name']}")
        result_file=RUNS/f"g3a-straight-{case['name']}-result-v1.hdf5"
        job=web.Job(simulation=simulation,task_name=item["task_name"],folder_name="P6 Physical Validation",task_id_cached=item["task_id"],verbose=False)
        data=job.run(path=result_file)
        metrics=_sparams(data)
        results.append({**case,"task_id":item["task_id"],"task_status":str(job.get_info().status),"result_file":result_file.name,"result_sha256":hashlib.sha256(result_file.read_bytes()).hexdigest(),"actual_flexcredits":float(job.real_cost(verbose=False)),"metrics":metrics})
    by_name={item["name"]:item for item in results}
    center=6
    convergence={}
    for length in (4,8):
        medium=by_name[f"length{length}_m20"]["metrics"]
        fine=by_name[f"length{length}_m25"]["metrics"]
        t20=complex(**medium["s21"][center])
        t25=complex(**fine["s21"][center])
        convergence[str(length)]={"insertion_loss_delta_db":abs(medium["transmission_db"][center]-fine["transmission_db"][center]),"phase_delta_deg":float(abs(np.angle(t20/t25,deg=True))),"fine_max_abs_energy_residual":fine["max_abs_energy_residual"],"fine_worst_reflection_db":fine["worst_reflection_db"]}
        convergence[str(length)]["passed"]=convergence[str(length)]["insertion_loss_delta_db"]<0.02 and convergence[str(length)]["phase_delta_deg"]<0.5 and fine["max_abs_energy_residual"]<0.01 and fine["worst_reflection_db"]<-30.0
    return {"name":"p6-g3a-straight-convergence-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"results":results,"convergence":convergence,"g3a_passed":all(item["passed"] for item in convergence.values()),"actual_total_flexcredits":sum(item["actual_flexcredits"] for item in results)}


def main()->None:
    parser=argparse.ArgumentParser(); mode=parser.add_mutually_exclusive_group(required=True); mode.add_argument("--upload-estimates",action="store_true"); mode.add_argument("--execute",action="store_true"); parser.add_argument("--user-credit-approval",action="store_true"); parser.add_argument("--user-solve-approval",action="store_true"); args=parser.parse_args()
    print(json.dumps(estimate(approved=args.user_credit_approval) if args.upload_estimates else execute(approved=args.user_solve_approval),indent=2))


if __name__=="__main__": main()
