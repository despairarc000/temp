"""R048 original-only static GCloud serialized-init route and virtual setter audit.

Requires private original libapollo.so. No runtime execution, route values or
authentication evidence. Designed to fail closed on any other version.
"""
import argparse,hashlib,json,re,shutil,struct,subprocess
from pathlib import Path
SHA="4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8"
SIZE=5243704
VTABLE_ADDRESS_POINT=0x4f5b6c
VTABLE_SET_ROUTE_SLOT=0x20
VTABLE_SET_ROUTE_THUMB=0x3c5b19
PINS=(
("factory_name_kind4",0x398d2a,"cmp","r0, #0x4"),
("factory_name_alloc_34",0x398d66,"movs","r0, #0x34"),
("factory_name_constructor",0x398d6e,"bl","0x398cb4"),
("init_dynamic_type_check",0x3c6106,"bl","0x3c9b48"),
("init_route_pointer_field",0x3c6164,"ldr","r2, [r5, #0x48]"),
("init_route_nonnull_gate",0x3c6168,"cbz","r2, 0x3c617c"),
("init_vtable_pointer",0x3c616a,"ldr","r3, [r4]"),
("init_result_this",0x3c616e,"mov","r1, r4"),
("init_out_result",0x3c6170,"mov","r0, r5"),
("init_virtual_slot20",0x3c6172,"ldr","r3, [r3, #0x20]"),
("init_virtual_route_call",0x3c6174,"blx","r3"),
("read_route_type_integer",0x398dda,"bl","0x36f190"),
("read_route_kind",0x398dde,"ldr","r0, [r4, #0x44]"),
("read_route_object_factory",0x398de0,"bl","0x398d24"),
("read_route_pointer_store",0x398de6,"str","r0, [r4, #0x48]"),
("read_optional_route_body",0x398dec,"bl","0x38fcb6"),
("write_optional_route_pointer",0x398b6c,"ldr","r1, [r5, #0x48]"),
("write_route_kind",0x398b72,"ldr","r1, [r1, #0xc]"),
("write_route_serialized_body",0x398b7c,"bl","0x38fd46"),
("connector_clone_route_vtable_slot",0x3c5b36,"ldr","r3, [r3, #0xc]"),
("connector_store_owned_route",0x3c5b3c,"str.w","r0, [r4, #0x19c]"),
("connect_load_owned_route",0x3c6c0c,"ldr.w","r1, [r6, #0x19c]"),
("connect_apply_owned_route",0x3c6c4a,"bl","0x3a33a0"),
)
WINDOWS=((0x398d24,0x398d30),(0x398d66,0x398d72),(0x398b6c,0x398b80),
 (0x398dd8,0x398df0),(0x3c5b32,0x3c5b40),
 (0x3c6104,0x3c610c),(0x3c6162,0x3c6178),
 (0x3c6c0a,0x3c6c10),(0x3c6c46,0x3c6c4e))
LINE=re.compile(r"^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$")
def parse(lines):
    found={}
    for s in lines:
        m=LINE.match(s)
        if m:
            a=int(m[1],16)
            if a in found:raise ValueError("duplicate instruction address")
            found[a]=(m[2].lower()," ".join(m[3].split("@")[0].split("<")[0].split()))
    return found
def failures(insns):
    return [name for name,a,op,args in PINS if insns.get(a)!=(op,args)]
def vtable_pointer(raw):
    # Original .data.rel.ro has virtual address - file offset = 0x1000.
    return struct.unpack_from("<I",raw,VTABLE_ADDRESS_POINT+VTABLE_SET_ROUTE_SLOT-0x1000)[0]
def audit(path):
    lib=Path(path)
    if not lib.is_file():raise ValueError("original private ELF missing")
    raw=lib.read_bytes()
    if len(raw)!=SIZE or hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("exact hash-pinned original required")
    if vtable_pointer(raw)!=VTABLE_SET_ROUTE_THUMB:
        raise ValueError("original SetRouteInfo vtable slot mismatch")
    if struct.unpack_from("<I",raw,0x4f5b68-0x1000)[0]!=0x4f5b0c:
        raise ValueError("unexpected vtable typeinfo")
    if struct.unpack_from("<I",raw,VTABLE_ADDRESS_POINT-0x1000)[0]!=0x3c7ae9:
        raise ValueError("unexpected vtable destructor")
    exe=shutil.which("llvm-objdump")
    if not exe:raise RuntimeError("llvm-objdump missing")
    instructions={}
    for start,end in WINDOWS:
        p=subprocess.run((exe,"--triple=thumbv7a-linux-gnueabihf","--disassemble",
         f"--start-address={start:#x}",f"--stop-address={end:#x}",str(lib)),
         capture_output=True,text=True,check=True,timeout=15)
        got=parse(p.stdout.splitlines())
        if not got or set(got)&set(instructions):
            raise ValueError("empty or overlapping disassembly window")
        instructions.update(got)
    bad=failures(instructions)
    return {"evidence":"EXACT_ORIGINAL_APOLLO_STATIC","pins":len(PINS),
      "passed":len(PINS)-len(bad),"failed":bad,
      "vtable_slot_0x20_matches_setroute":True,
      "serialized_route_kind_field":"0x44",
      "optional_init_route_pointer":"0x48",
      "cloned_connector_route_pointer":"0x19c",
      "runtime_route_value":"UNKNOWN","phone_callback_observed":False,
      "authenticated_login":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--original-lib",required=True)
    a=p.parse_args()
    try:r=audit(a.original_lib)
    except (ValueError,RuntimeError,OSError,subprocess.SubprocessError) as e:
        print(json.dumps({"status":"REFUSED","reason":type(e).__name__}))
        raise SystemExit(2)
    print(json.dumps(r,indent=2))
    raise SystemExit(bool(r["failed"]))
