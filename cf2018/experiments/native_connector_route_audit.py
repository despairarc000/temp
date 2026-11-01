"""R045: read-only, exact original Apollo connector route audit. No network or payload export."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
SHA256='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
SIZE=5243704
PINS=(
('native_initialize_get_apollo',0x38c8d8,'bl','0x380c48'),
('native_initialize_virtual_create',0x38c8e8,'blx','r12'),
('connector_init_save_kind',0x38265c,'str','r1, [r0, #0x20]'),
('connector_init_save_name',0x382664,'bl','0x3f96c0'),
('connector_on_connect_alloc_tgcp',0x382d24,'bl','0x37d824'),
('connector_on_connect_add_observer',0x382d30,'bl','0x37dcd0'),
('type3_name_route_collection',0x382dd0,'cmp','r2, #0x3'),
('named_route_type4_check',0x382df2,'cmp','r3, #0x4'),
('named_route_extract_value',0x382df8,'bl','0x3972f4'),
('named_route_verify_type4',0x382e1e,'cmp','r3, #0x4'),
('named_route_measure_size',0x382e24,'bl','0x3972f0'),
('named_route_pointer_check',0x382e2a,'cmp.w','r8, #0x0'),
('named_route_nonempty_check',0x382e36,'cmp','r0, #0x0'),
('name_route_tgcp_initialize',0x382ea0,'bl','0x37bfe4'),
('conditional_routeinfo_gate',0x3831a0,'cbz','r1, 0x3831aa'),
('optional_routeinfo_apply',0x3831a6,'bl','0x37a764'),
('connection_start',0x383204,'bl','0x37ad40'),
)
WINDOWS=((0x382658,0x38266c),(0x382d20,0x382d34),(0x382dcc,0x382dd4),
(0x382dee,0x382e38),(0x382e9a,0x382ea4),(0x38319c,0x3831ac),
(0x3831fc,0x383208),(0x38c8d4,0x38c8ec))
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')
def parse(source):
 out={}
 for line in source.splitlines():
  m=LINE.match(line)
  if m:
   addr=int(m[1],16)
   if addr in out:raise ValueError('duplicate instruction')
   out[addr]=(m[2].lower(),' '.join(m[3].split('@')[0].split('<')[0].split()))
 return out
def failures(insns):
 return [n for n,a,op,args in PINS if insns.get(a)!=(op,args)]
def audit(source):
 f=Path(source)
 if not f.is_file() or f.stat().st_size!=SIZE or hashlib.sha256(f.read_bytes()).hexdigest()!=SHA256:
  raise ValueError('exact original Apollo binary required')
 exe=shutil.which('llvm-objdump')
 if not exe:raise RuntimeError('llvm-objdump required')
 insns={}
 for start,end in WINDOWS:
  p=subprocess.run((exe,'--triple=thumbv7a-linux-gnueabihf','--disassemble',
   f'--start-address={start:#x}',f'--stop-address={end:#x}',str(f)),
   capture_output=True,text=True,check=True,timeout=15)
  part=parse(p.stdout)
  if not part or set(part)&set(insns):raise ValueError('ambiguous disassembly window')
  insns.update(part)
 bad=failures(insns)
 return {'evidence':'ORIGINAL_APOLLO_STATIC','pins':len(PINS),'passed':len(PINS)-len(bad),
  'failed':bad,'name_route_type4':'VERIFIED','route_name_value':'NOT_OBSERVED',
  'routeinfo_apply':'CONDITIONAL','start_after_init':'VERIFIED',
  'client_session_acceptance':'UNPROVEN','login_or_gameplay':'UNPROVEN'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-lib',required=True);a=p.parse_args()
 try:r=audit(a.original_lib)
 except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:
  print(json.dumps({'status':'REFUSED','reason':type(e).__name__}));raise SystemExit(2)
 print(json.dumps(r,indent=2))
 raise SystemExit(bool(r['failed']))
