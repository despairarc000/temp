"""R047: hash-pinned original GCloud connector route clone to TGCP.
Static evidence only: no real-game callback, accepted ACK, or route name inferred.
"""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
SHA="4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8";SIZE=5243704
PINS=(
("getter_prior_route",0x3c5b1c,"ldr.w","r0, [r1, #0x19c]"),
("get_clone_vtable",0x3c5b32,"ldr","r3, [r6]"),
("clone_vtable_slot",0x3c5b36,"ldr","r3, [r3, #0xc]"),
("clone_call",0x3c5b38,"blx","r3"),
("store_clone",0x3c5b3c,"str.w","r0, [r4, #0x19c]"),
("construct_gcloud_tgcp",0x3c6956,"bl","0x3a62a0"),
("store_gcloud_tgcp",0x3c695e,"str.w","r4, [r6, #0x198]"),
("optional_nameservice",0x3c696a,"bl","0x3a3374"),
("route_clone_load",0x3c6c0c,"ldr.w","r1, [r6, #0x19c]"),
("route_guard",0x3c6c10,"cbnz","r1, 0x3c6c46"),
("tgcp_object_load",0x3c6c46,"ldr.w","r0, [r6, #0x198]"),
("apply_cloned_route",0x3c6c4a,"bl","0x3a33a0"),
("start_endpoint",0x3c6c82,"ldr.w","r2, [r6, #0x1b8]"),
("start_gcloud_tgcp",0x3c6c86,"bl","0x3a369c"),
)
WINDOWS=((0x3c5b1a,0x3c5b40),(0x3c6954,0x3c696e),
 (0x3c6c0a,0x3c6c14),(0x3c6c44,0x3c6c4e),(0x3c6c80,0x3c6c8a))
LINE=re.compile(r"^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$")
def parse(text):
    found={}
    for row in text.splitlines():
        m=LINE.match(row)
        if m:
            a=int(m[1],16)
            if a in found:raise ValueError("duplicate instruction")
            found[a]=(m[2].lower()," ".join(m[3].split("@")[0].split("<")[0].split()))
    return found
def failures(insns):return [name for name,a,op,args in PINS if insns.get(a)!=(op,args)]
def audit(path):
    f=Path(path)
    if not f.is_file() or f.stat().st_size!=SIZE or hashlib.sha256(f.read_bytes()).hexdigest()!=SHA:
        raise ValueError("exact Apollo original required")
    exe=shutil.which("llvm-objdump")
    if not exe:raise RuntimeError("llvm-objdump missing")
    result={}
    for start,end in WINDOWS:
        p=subprocess.run((exe,"--triple=thumbv7a-linux-gnueabihf","--disassemble",
          f"--start-address={start:#x}",f"--stop-address={end:#x}",str(f)),
          capture_output=True,text=True,check=True,timeout=15)
        part=parse(p.stdout)
        if not part or set(part)&set(result):raise ValueError("empty or overlapping disassembly")
        result.update(part)
    bad=failures(result)
    return {"evidence":"ORIGINAL_NATIVE_STATIC","checks":len(PINS),
      "passed":len(PINS)-len(bad),"failed":bad,
      "route_object":"CLONED_AND_STORED_AT_CONNECTOR_0x19c",
      "connector_calls_gcloud_setroute":True,
      "caller_that_creates_route":"UNKNOWN",
      "route_name_value":"UNKNOWN","live_result":"NOT_TESTED"}
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--original-lib",required=True)
    args=parser.parse_args()
    try:v=audit(args.original_lib)
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:
        print(json.dumps({"status":"REFUSED","reason":type(e).__name__}));raise SystemExit(2)
    print(json.dumps(v,indent=2));raise SystemExit(bool(v["failed"]))
