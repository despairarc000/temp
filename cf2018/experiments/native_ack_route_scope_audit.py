"""R042 original Apollo read-only TGCP ACK-head / client ACK-gate audit.

No native execution. ACK-head serializer has no route field, but outer/session
and key acceptance remain unknown. Do not auto-ACK shorter-route SYNs.
"""
import hashlib,re,shutil,subprocess
from pathlib import Path
ORIGINAL_SHA='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
ORIGINAL_SIZE=5243704
PINS=(
 ('field1',0x3b58d8,'movs','r1, #0x11'),
 ('field2',0x3b58f0,'movs','r1, #0x21'),
 ('field3_key',0x3b5908,'movs','r1, #0x35'),
 ('key_response_serializer',0x3b5926,'bl','0x3afefa'),
 ('field4',0x3b593c,'movs','r1, #0x41'),
 ('field5',0x3b5952,'movs','r1, #0x50'),
 ('field6',0x3b5968,'movs','r1, #0x60'),
 ('default_window',0x3b589a,'mov.w','r3, #0x400'),
 ('client_ack_selector',0x3ac106,'movw','r4, #0x1002'),
 ('client_ack_compare',0x3ac116,'cmpeq','r2, r4'),
 ('client_ack_branch',0x3ac11c,'beq','0x3ac126'),
 ('client_ack_body_decode',0x3ac1b6,'bl','0x3b8860'),
)
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')
def parse(lines):
    out={}
    for line in lines:
        m=LINE.match(line)
        if m:
            a=int(m.group(1),16)
            if a in out:raise ValueError('duplicate address')
            out[a]=(m.group(2).lower(),' '.join(m.group(3).split('@')[0].split('<')[0].split()))
    return out
def failures(insns):
    return [name for name,a,op,args in PINS if insns.get(a)!=(op,args)]
def audit(path):
    f=Path(path)
    if f.stat().st_size!=ORIGINAL_SIZE or hashlib.sha256(f.read_bytes()).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('requires exact original libapollo.so')
    exe=shutil.which('llvm-objdump')
    if exe is None:raise RuntimeError('llvm-objdump required')
    insns={}
    for start,end in [(0x3b587c,0x3b5980),(0x3ac100,0x3ac126),(0x3ac1ae,0x3ac1be)]:
        p=subprocess.run([exe,'--triple=thumbv7a-linux-gnueabihf','--disassemble',
            f'--start-address={start:#x}',f'--stop-address={end:#x}',str(f)],
            capture_output=True,text=True,check=True,timeout=10)
        part=parse(p.stdout.splitlines())
        if not part or set(part)&set(insns):raise ValueError('invalid/overlapping windows')
        insns.update(part)
    bad=failures(insns)
    serializer={a:(op,args) for a,(op,args) in insns.items() if 0x3b58d0<=a<0x3b5980}
    route_calls=[(a,args) for a,(op,args) in serializer.items()
                 if op.startswith('bl') and ('0x3b2222' in args or 'RouteInfo' in args)]
    if route_calls:bad.append('unexpected_direct_route_serializer')
    return {'checked':len(PINS),'passed':len(PINS)-len([x for x in bad if x!='unexpected_direct_route_serializer']),
        'failures':bad,'ack_head_field_tags':['0x11','0x21','0x35','0x41','0x50','0x60'],
        'ack_head_has_route_field14':False,'direct_route_serializer_calls':len(route_calls),
        'client_expects_ack_type_0x1002':True,'auth_or_route_acceptance_proven':False}
if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--original-lib',required=True)
    args=p.parse_args()
    try:x=audit(args.original_lib)
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        print(json.dumps({'status':'REFUSED','reason':type(exc).__name__}));raise SystemExit(2)
    print(json.dumps(x,indent=2));raise SystemExit(bool(x['failures']))
