"""Generate and independently re-read the exact P6 serial Archimedean spiral."""
from __future__ import annotations
import csv, hashlib, json, math, struct
from datetime import datetime
from pathlib import Path
from typing import Iterable

HERE=Path(__file__).resolve().parent;OUT=HERE/"layout";RUNS=HERE/"runs"
TARGET_UM=142401.41755;PITCH_UM=5.0;WIDTH_UM=.343;MIN_RADIUS_UM=10.0;MIN_DRC_GAP_UM=.2;DBU_UM=.001;NG=4.012965400696482;C_UM_PER_PS=299.792458

def curvature_radius(r:float,b:float)->float:return (r*r+b*b)**1.5/(r*r+2*b*b)
def inner_radius(b:float)->float:
    lo,hi=MIN_RADIUS_UM,MIN_RADIUS_UM+2
    for _ in range(80):
        mid=(lo+hi)/2
        if curvature_radius(mid,b)<MIN_RADIUS_UM:lo=mid
        else:hi=mid
    return hi
def arc_at(theta:float,r0:float,b:float)->float:
    def f(r):return .5/b*(r*math.sqrt(r*r+b*b)+b*b*math.asinh(r/b))
    return f(r0+b*theta)-f(r0)
def invert_arc(length:float,r0:float,b:float,hi:float)->float:
    lo=0.0
    for _ in range(90):
        mid=(lo+hi)/2
        if arc_at(mid,r0,b)<length:lo=mid
        else:hi=mid
    return (lo+hi)/2
def centerline(theta_end:float,r0:float,b:float,step_um:float=2.0):
    pts=[];t=0.0
    while t<theta_end:
        r=r0+b*t;pts.append((r*math.cos(t),r*math.sin(t),t));t=min(theta_end,t+step_um/math.sqrt(r*r+b*b))
    r=r0+b*theta_end;pts.append((r*math.cos(theta_end),r*math.sin(theta_end),theta_end));return pts
def rec(rt:int,dt:int,payload:bytes=b"")->bytes:
    if len(payload)%2:payload+=b"\0"
    return struct.pack(">HBB",4+len(payload),rt,dt)+payload
def gds_real8(x:float)->bytes:
    if x==0:return b"\0"*8
    sign=0x80 if x<0 else 0;x=abs(x);exp=64
    while x>=1:x/=16;exp+=1
    while x<1/16:x*=16;exp-=1
    mant=min(int(x*(1<<56)),(1<<56)-1);return bytes([sign|exp])+mant.to_bytes(7,"big")
def write_gds(points:list[tuple[float,float,float]],path:Path):
    now=datetime.now();stamp=struct.pack(">12h",*(now.year,now.month,now.day,now.hour,now.minute,now.second)*2);data=bytearray();data+=rec(0x00,0x02,struct.pack(">h",600));data+=rec(0x01,0x02,stamp);data+=rec(0x02,0x06,b"P6_PHYSICAL");data+=rec(0x03,0x05,gds_real8(1e-6)+gds_real8(1e-9));data+=rec(0x05,0x02,stamp);data+=rec(0x06,0x06,b"DELAY_SPIRAL")
    xy=[(round(x/DBU_UM),round(y/DBU_UM)) for x,y,_ in points]
    for start in range(0,len(xy)-1,8000):
        chunk=xy[start:min(start+8001,len(xy))];payload=b"".join(struct.pack(">ii",x,y) for x,y in chunk);data+=rec(0x09,0x00);data+=rec(0x0d,0x02,struct.pack(">h",1));data+=rec(0x0e,0x02,struct.pack(">h",0));data+=rec(0x0f,0x03,struct.pack(">i",round(WIDTH_UM/DBU_UM)));data+=rec(0x10,0x03,payload);data+=rec(0x11,0x00)
    data+=rec(0x07,0x00);data+=rec(0x04,0x00);path.write_bytes(data)
def read_gds_xy(path:Path):
    raw=path.read_bytes();i=0;paths=[]
    while i<len(raw):
        n,rt,dt=struct.unpack(">HBB",raw[i:i+4]);payload=raw[i+4:i+n]
        if rt==0x10:paths.append([(x*DBU_UM,y*DBU_UM) for x,y in struct.iter_unpack(">ii",payload)])
        i+=n
    return paths
def polyline_length(paths:Iterable[list[tuple[float,float]]])->float:
    return sum(math.hypot(x2-x1,y2-y1) for p in paths for (x1,y1),(x2,y2) in zip(p,p[1:]))
def generate():
    OUT.mkdir(exist_ok=True);b=PITCH_UM/(2*math.pi);r0=inner_radius(b);lo,hi=0.0,2*math.pi*200
    while arc_at(hi,r0,b)<TARGET_UM:hi*=2
    theta=invert_arc(TARGET_UM,r0,b,hi);pts=centerline(theta,r0,b);taps=[]
    for k in range(20):
        s=TARGET_UM*k/19;t=invert_arc(s,r0,b,theta);r=r0+b*t;taps.append({"tap":k,"distance_um":s,"x_um":r*math.cos(t),"y_um":r*math.sin(t),"target_delay_ps":100*k,"predicted_delay_ps":NG*s/C_UM_PER_PS})
    csv_path=OUT/"spiral-centerline-v1.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(["x_um","y_um","theta_rad"]);w.writerows(pts)
    gds_path=OUT/"spiral-centerline-v1.gds";write_gds(pts,gds_path);gds_paths=read_gds_xy(gds_path);gds_len=polyline_length(gds_paths);outer=r0+b*theta;join_gap=max((math.hypot(a[-1][0]-b_[0][0],a[-1][1]-b_[0][1]) for a,b_ in zip(gds_paths,gds_paths[1:])),default=0.0)
    stride=max(1,len(pts)//5000);view=pts[::stride]+[pts[-1]];scale=900/(2*(outer+15));coords=" ".join(f"{450+x*scale:.3f},{450-y*scale:.3f}" for x,y,_ in view);svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900" viewBox="0 0 900 900"><rect width="900" height="900" fill="white"/><polyline points="{coords}" fill="none" stroke="#155eef" stroke-width="1"/></svg>';svg_path=OUT/"spiral-centerline-v1.svg";svg_path.write_text(svg,encoding="utf-8")
    result={"name":"p6-g2-spiral-layout-v1","topology":"single-series Archimedean spiral with 20 progressive taps","selection_note":"selected instead of provisional double spiral to avoid a central U-turn below the accepted bend radius; no P5 score used","target_centerline_um":TARGET_UM,"analytic_centerline_um":arc_at(theta,r0,b),"gds_quantized_polyline_um":gds_len,"relative_length_error":abs(gds_len-TARGET_UM)/TARGET_UM,"pitch_um":PITCH_UM,"waveguide_width_um":WIDTH_UM,"minimum_drc_gap_um":MIN_DRC_GAP_UM,"edge_gap_um":PITCH_UM-WIDTH_UM,"inner_centerline_radius_um":r0,"minimum_curvature_radius_um":curvature_radius(r0,b),"outer_centerline_radius_um":outer,"turns":theta/(2*math.pi),"die_bbox_um":[2*(outer+15),2*(outer+15)],"max_parallel_segment_upper_bound_um":2*math.pi*outer,"tap_spacing_um":TARGET_UM/19,"predicted_total_delay_ps":NG*TARGET_UM/C_UM_PER_PS,"taps":taps,"gds":{"path_elements":len(gds_paths),"maximum_join_gap_um":join_gap,"database_unit_um":DBU_UM},"drc":{"length_within_0p1_percent":abs(gds_len-TARGET_UM)/TARGET_UM<.001,"minimum_radius_passed":curvature_radius(r0,b)>=MIN_RADIUS_UM,"edge_gap_passed":PITCH_UM-WIDTH_UM>=MIN_DRC_GAP_UM,"gds_path_continuity_passed":join_gap<=DBU_UM,"tap_count_passed":len(taps)==20},"files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (csv_path,gds_path,svg_path)}};result["passed"]=all(result["drc"].values());return result
if __name__=="__main__":
    result=generate();(RUNS/"g2-spiral-layout-result-v1.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
