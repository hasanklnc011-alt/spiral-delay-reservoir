"""Cost-gated missing m15 lossless straight references for bend de-embedding."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
from tidy3d import web
from g3_straight_preflight import HERE
from g3_straight_preflight_v2 import build_straight_v2
from g3_straight_cloud import PER_SOURCE_LIMIT_FC, TOTAL_LIMIT_FC, _sparams
RUNS=HERE/"runs";ESTIMATE_RECORD=RUNS/"g3a-straight-lossless-m15-estimate-v1.json"
def cases():return [{"name":f"length{x}_m15","length_um":float(x)} for x in (4,8)]
def build(c):
    s=build_straight_v2(c["length_um"],15.0);return s,hashlib.sha256(s.model_dump_json().encode()).hexdigest()
def estimate(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User credit approval required")
    jobs=[]
    for c in cases():
        s,d=build(c);n=f"p6_g3a_lossless_{c['name']}";j=web.Job(simulation=s,task_name=n,folder_name="P6 Physical Validation",verbose=False);j.upload();jobs.append({**c,"task_name":n,"task_id":str(j.task_id),"task_status":str(j.get_info().status),"serialized_simulation_sha256":d,"estimated_flexcredits":float(j.estimate_cost(verbose=False)),"solve_started":False})
    total=sum(x["estimated_flexcredits"] for x in jobs);return {"name":"p6-g3a-straight-lossless-m15-estimate-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"jobs":jobs,"estimated_total_flexcredits":total,"within_limits":total<TOTAL_LIMIT_FC and all(x["estimated_flexcredits"]<PER_SOURCE_LIMIT_FC for x in jobs)}
def execute(*,approved:bool)->dict[str,Any]:
    if not approved:raise PermissionError("User solve approval required")
    rec=json.loads(ESTIMATE_RECORD.read_text(encoding="utf-8"));locked={x["name"]:x for x in rec["jobs"]};out=[]
    if not rec["within_limits"]:raise RuntimeError("m15 straight suite exceeds limits")
    for c in cases():
        x=locked[c["name"]];s,d=build(c)
        if x["solve_started"] or d!=x["serialized_simulation_sha256"]:raise RuntimeError("locked mismatch")
        p=RUNS/f"g3a-lossless-{c['name']}-result-v1.hdf5";j=web.Job(simulation=s,task_name=x["task_name"],folder_name="P6 Physical Validation",task_id_cached=x["task_id"],verbose=False);m=_sparams(j.run(path=p));out.append({**c,"task_id":x["task_id"],"task_status":str(j.get_info().status),"result_file":p.name,"result_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actual_flexcredits":float(j.real_cost(verbose=False)),"metrics":m})
    return {"name":"p6-g3a-straight-lossless-m15-result-v1","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"results":out,"actual_total_flexcredits":sum(x["actual_flexcredits"] for x in out)}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument("--upload-estimate",action="store_true");g.add_argument("--execute",action="store_true");p.add_argument("--user-credit-approval",action="store_true");p.add_argument("--user-solve-approval",action="store_true");a=p.parse_args();print(json.dumps(estimate(approved=a.user_credit_approval) if a.upload_estimate else execute(approved=a.user_solve_approval),indent=2))
if __name__=="__main__":main()
