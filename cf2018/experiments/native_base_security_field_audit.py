"""R032: Read-only original TGCPBase field6 inbound decrypt-mode audit.

Exact owner-provided Apollo only. No native execution, packet/key output or send.
"""
import hashlib,re,shutil,subprocess
from pathlib import Path
SHA='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
SIZE=5243704
PINS=(
 ('base_field_number',0x3af504,'lsrs','r3, r1, #0x4'),
 ('base_field_index',0x3af506,'subs','r3, #0x1'),
 ('base_field_jump_table',0x3af50c,'tbb','[pc, r3]'),
 ('field6_object_offset',0x3af580,'add.w','r1, r4, #0xc'),
 ('field6_u8_reader',0x3af58e,'bl','0x1f4842'),
 ('inbound_parsed_header_at_720',0x3ab6d0,'add.w','r3, r4, #0x720'),
 ('inbound_mode_from_header_at_72c',0x3abf4e,'ldrb.w','r11, [r4, #0x72c]'),
 ('inbound_mode_compare_zero',0x3abf5c,'cmp.w','r11, #0x0'),
 ('inbound_clear_copy_branch',0x3abf60,'beq','0x3abfb2'),
 ('outgoing_base_mode_set_zero',0x3aabec,'strb','r3, [r1, #0xc]'),
)
WINDOWS=((0x3af500,0x3af510),(0x3af57c,0x3af594),
 (0x3ab6cc,0x3ab6d6),(0x3abf4c,0x3abf64),(0x3aabe6,0x3aabee))
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')
def parse_instructions(source):
    found={}
    for line in source.splitlines():
        m=LINE.match(line)
        if m:
            address=int(m[1],16)
            if address in found:raise ValueError('duplicate native instruction')
            found[address]=(m[2].lower(),' '.join(m[3].split('@')[0].split('<')[0].split()))
    return found
def failures(insns):
    return [name for name,addr,mnemonic,operand in PINS
            if insns.get(addr)!=(mnemonic,operand)]
def audit(path):
    path=Path(path);raw=path.read_bytes()
    if len(raw)!=SIZE or hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError('exact original source required')
    # TGCPBase switch: field6 -> index5 -> table byte 0x36 -> 0x3af57c.
    if raw[0x3af515]!=0x36 or 0x3af510+2*raw[0x3af515]!=0x3af57c:
        raise ValueError('native switch dispatch mismatch')
    exe=shutil.which('llvm-objdump')
    if not exe:raise ValueError('llvm-objdump required')
    instructions={}
    for begin,end in WINDOWS:
        r=subprocess.run([exe,'--triple=thumbv7a-linux-gnueabihf',
             '--disassemble','--start-address='+hex(begin),
             '--stop-address='+hex(end),str(path)],
             capture_output=True,text=True,check=True,timeout=12)
        part=parse_instructions(r.stdout)
        if not part or set(part).intersection(instructions):
            raise ValueError('ambiguous native instruction window')
        instructions.update(part)
    bad=failures(instructions)
    return {'source':'PINNED_ORIGINAL_NATIVE_STATIC','checks':len(PINS)+1,
      'passed':len(PINS)+1-len(bad),'failed':bad,
      'tgcp_base_field6_dispatch_verified':True,
      'inbound_decrypt_selector_source':'DECODED_PER_FRAME_BASE_FIELD6',
      'clear_copy_when_field6_zero':True,
      'real_phone_inbound_mode_measured':False,'reply_sent':False}
if __name__=='__main__':
 import argparse,json
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--lib',required=True)
 a=p.parse_args()
 try:r=audit(a.lib)
 except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as ex:
  print(json.dumps({'status':'REFUSED','reason':type(ex).__name__}));raise SystemExit(2)
 print(json.dumps(r,indent=2))
 raise SystemExit(bool(r['failed']))
