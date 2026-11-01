"""R040 read-only original Apollo type 0x5001/0x5002 static audit."""
import hashlib,re,shutil,subprocess
from pathlib import Path
SHA256='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
SIZE=5243704
PINS=(
('stop_requires_state5',0x3a96e2,'cmp','r3, #0x5'),
('stop_magic_4366',0x3a96ea,'movw','r1, #0x4366'),
('stop_header_type_5001',0x3a970a,'movw','r3, #0x5001'),
('stop_header_store',0x3a970e,'strh','r3, [r2, #0x6]'),
('stop_body_type_5001',0x3a9724,'movw','r2, #0x5001'),
('stop_body_pack',0x3a9730,'bl','0x3b83ec'),
('stop_send_frame',0x3a974e,'bl','0x3ab430'),
('stop_state6',0x3a9754,'movs','r3, #0x6'),
('stop_state_store',0x3a9756,'str.w','r3, [r4, #0x6c8]'),
('receiver_type_5002',0x3aa1a2,'movw','r3, #0x5002'),
('receiver_compare_5002',0x3aa1a6,'cmp','r6, r3'),
('receiver_get_packet',0x3aa1b2,'bl','0x3abe34'),
('receiver_handle_stop',0x3aa1c2,'bl','0x3aafe0'),
)
WINDOWS=((0x3a96de,0x3a96f0),(0x3a9706,0x3a9712),
(0x3a9720,0x3a9734),(0x3a974a,0x3a975a),
(0x3aa19e,0x3aa1aa),(0x3aa1ae,0x3aa1b8),(0x3aa1be,0x3aa1c6))
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')
def parse(source):
    found={}
    for line in source.splitlines():
        m=LINE.match(line)
        if m:
            a=int(m[1],16)
            if a in found:raise ValueError('duplicate instruction')
            found[a]=(m[2].lower(),' '.join(m[3].split('@')[0].split('<')[0].split()))
    return found
def failures(insns):
    return [name for name,a,op,args in PINS if insns.get(a)!=(op,args)]
def audit(path):
    path=Path(path)
    if path.stat().st_size!=SIZE or hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:
        raise ValueError('exact original Apollo required')
    objdump=shutil.which('llvm-objdump')
    if not objdump:raise ValueError('llvm-objdump unavailable')
    insns={}
    for start,end in WINDOWS:
        proc=subprocess.run((objdump,'--triple=thumbv7a-linux-gnueabihf',
         '--disassemble',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(path)),
         capture_output=True,text=True,check=True,timeout=15)
        part=parse(proc.stdout)
        if not part or set(part).intersection(insns):raise ValueError('ambiguous window')
        insns.update(part)
    bad=failures(insns)
    return {'source':'ORIGINAL_APOLLO_STATIC','checks':len(PINS),
        'passed':len(PINS)-len(bad),'failed':bad,
        '0x5001':'CLIENT_STOP_SESSION_PACKET_CONSTRUCTION',
        '0x5002':'STOP_SESSION_RESPONSE_DISPATCH',
        'phone_5001_same_callsite_proven':False,'authenticated_or_playable':False}
if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument('--lib',required=True)
    args=p.parse_args()
    try:r=audit(args.lib)
    except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'status':'REFUSED','reason':type(e).__name__}))
        raise SystemExit(2)
    print(json.dumps(r,indent=2))
    raise SystemExit(bool(r['failed']))
