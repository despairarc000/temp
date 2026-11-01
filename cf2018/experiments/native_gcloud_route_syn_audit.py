"""R046: exact original Apollo, read-only GCloud named-route transport/SYN audit.

Only confirms STATIC instruction path; does not identify the 10-byte route,
prove phone execution, login, accepted ACK or playable matches.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
SHA256="4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8"
SIZE=5243704
# name, Thumb instruction address, mnemonic, normalized operands
PINS=(
("gcloud_route_kind_load",0x3a33f2,"ldr","r6, [r1, #0xc]"),
("gcloud_type4_gate",0x3a33fa,"cmp","r6, #0x4"),
("gcloud_name_input",0x3a347e,"add.w","r0, r1, #0x10"),
("gcloud_name_c_str",0x3a3482,"bl","0x3972f4"),
("gcloud_name_max80",0x3a3486,"movs","r2, #0x80"),
("gcloud_to_transport_api",0x3a34d0,"bl","0x3a9d02"),
("transport_route_type4_gate",0x3a9d1e,"cmp","r1, #0x4"),
("transport_route_buffer3400",0x3a9d22,"add.w","r0, r0, #0x3400"),
("transport_type4_copy_size",0x3a9d2a,"movs","r2, #0x7f"),
("transport_route_type_store",0x3a9d50,"str","r5, [r4]"),
("syn_stored_type_load",0x3abb80,"ldr","r3, [r1]"),
("syn_type4_gate",0x3abb86,"cmp","r3, #0x4"),
("syn_name_source",0x3abba0,"add.w","r0, r5, #0x2dc0"),
("syn_type4_store",0x3abba4,"strb.w","r3, [r4, #0xaa1]"),
("syn_name_length_bound",0x3abbac,"movs","r2, #0x7f"),
("syn_name_copy",0x3abbae,"blx","0x193e48"),
("syn_name_terminate",0x3abbb2,"strb.w","r6, [r4, #0xb27]"),
("query_result_ok_gate",0x3a60ca,"cbnz","r1, 0x3a60fe"),
("query_result_array",0x3a60e4,"bl","0x395e1c"),
("query_result_selected_name",0x3a618a,"bl","0x3972f4"),
("query_result_endpoint_store",0x3a6194,"bl","0x3f8f7c"),
("thread_start_endpoint_load",0x3a4a7c,"ldr.w","r1, [r4, #0x2dc]"),
("thread_start_transport",0x3a4a80,"bl","0x3a9d92"),
("ack_type1002_gate",0x3ac106,"movw","r4, #0x1002"),
("ack_tgcp_body_unpack",0x3ac1b6,"bl","0x3b8860"),
("ack_body_result_check",0x3ac1ba,"cmp","r0, #0x0"),
)
WINDOWS=(
(0x3a33f0,0x3a33fe),(0x3a347c,0x3a348e),(0x3a34cc,0x3a34d4),
(0x3a9d1c,0x3a9d2e),(0x3a9d4c,0x3a9d54),
(0x3abb7e,0x3abb8a),(0x3abb9e,0x3abbb6),
(0x3a60c6,0x3a60ce),(0x3a60e0,0x3a60e8),(0x3a6188,0x3a6198),
(0x3a4a7c,0x3a4a84),(0x3ac104,0x3ac10c),(0x3ac1b4,0x3ac1be))
LINE=re.compile(r"^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$")
def parse(lines):
    result={}
    for line in lines:
        m=LINE.match(line)
        if m:
            address=int(m[1],16)
            if address in result: raise ValueError("duplicate disassembly address")
            result[address]=(m[2].lower()," ".join(m[3].split("@")[0].split("<")[0].split()))
    return result
def failures(insns):
    return [name for name,addr,opcode,args in PINS if insns.get(addr)!=(opcode,args)]
def audit(path):
    lib=Path(path)
    if not lib.is_file() or lib.stat().st_size!=SIZE or hashlib.sha256(lib.read_bytes()).hexdigest()!=SHA256:
        raise ValueError("exact original Apollo file required")
    exe=shutil.which("llvm-objdump")
    if not exe:raise RuntimeError("llvm-objdump unavailable")
    insns={}
    for start,end in WINDOWS:
        proc=subprocess.run((exe,"--triple=thumbv7a-linux-gnueabihf","--disassemble",
            f"--start-address={start:#x}",f"--stop-address={end:#x}",str(lib)),
            capture_output=True,text=True,check=True,timeout=15)
        part=parse(proc.stdout.splitlines())
        if not part or set(part)&set(insns):raise ValueError("empty or overlapping disassembly windows")
        insns.update(part)
    bad=failures(insns)
    return {"scope":"STATIC_ORIGINAL_GCLOUD","checks":len(PINS),
      "passed":len(PINS)-len(bad),"failed":bad,
      "gcloud_type4_route":"COPIED_INTO_TRANSPORT_AND_SYN",
      "query_result_endpoint":"STORED_THEN_USED_BY_THREAD_START",
      "ack_body":"PARSED_AFTER_TYPE1002_GATE",
      "caller_that_supplied_10_byte_name":"NOT_IDENTIFIED",
      "phone_runtime_chain":"UNPROVEN","game_login":"UNPROVEN"}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--original-lib",required=True);args=p.parse_args()
    try:r=audit(args.original_lib)
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as e:
        print(json.dumps({"status":"REFUSED","reason":type(e).__name__}));raise SystemExit(2)
    print(json.dumps(r,indent=2));raise SystemExit(bool(r["failed"]))
