"""R030: bounded original-native incoming 0x4013/uncompressed-path audit.

Read-only SHA-pinned static instructions, not native emulation or wire acceptance.
Only labels/counts exported. Original binary is supplied privately.
"""
import hashlib,re,shutil,subprocess
from pathlib import Path

SHA256='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
SIZE=5243704
PINS=(
('gather_32byte_header',0x3ab6a0,'cmp','r2, #0x20'),
('gather_read_magic',0x3ab6f6,'ldrh.w','r0, [r4, #0x720]'),
('gather_magic_4366',0x3ab6fa,'movw','r1, #0x4366'),
('gather_compare_magic',0x3ab6fe,'cmp','r0, r1'),
('gather_parse_tlv',0x3ab722,'bl','0x3aab44'),
('rx_calls_gather',0x3abe4c,'bl','0x3ab5ec'),
('rx_decrypt_state_flag',0x3abf4e,'ldrb.w','r11, [r4, #0x72c]'),
('rx_decrypt_call',0x3abf74,'bl','0x3ab31e'),
('rx_direct_copy',0x3abfe6,'blx','0x193ed8'),
('peek_requires_state5',0x3a8d1a,'cmp','r3, #0x5'),
('peek_rx_unpack',0x3a8d6e,'bl','0x3abe34'),
('peek_type_4013',0x3a8de4,'movw','r3, #0x4013'),
('peek_compare_type',0x3a8de8,'cmp','r6, r3'),
('peek_read_compression',0x3a8dec,'ldrb.w','r3, [r4, #0x740]'),
('peek_zero_skips_lz4',0x3a8df2,'beq','0x3a8ed4'),
('peek_compressed_calls_lz4',0x3a8e7c,'bl','0x286d7c'),
('peek_output_pointer',0x3a8edc,'str.w','r3, [r8]'),
('peek_output_length',0x3a8ee2,'str','r3, [r7]'),
('queue_source_pointer',0x3a4fee,'ldr','r1, [sp, #0x10]'),
('queue_length',0x3a4ff0,'mov','r2, r8'),
('enqueue_bytes',0x3a4ffe,'bl','0x1b397c'),
('read_dequeues',0x3a4018,'bl','0x1b37c8'),
('read_assigns',0x3a403c,'bl','0x397316'),
('app_sets_exact_bytes',0x39b9a0,'bl','0x3c180e'),
('app_reads_message_begin',0x39b9d4,'blx','r12'),
('app_finds_pending_rpc64',0x39b9f2,'bl','0x39a3c0'),
)
BOUNDS=((0x3ab69c,0x3ab6a6),(0x3ab6f4,0x3ab726),
(0x3abe46,0x3abe50),(0x3abf4a,0x3abf76),(0x3abfde,0x3abfea),
(0x3a8d16,0x3a8d20),(0x3a8d6a,0x3a8d76),(0x3a8de0,0x3a8dfa),
(0x3a8e78,0x3a8e84),(0x3a8ed8,0x3a8ee6),
(0x3a4fea,0x3a5002),(0x3a4014,0x3a4020),(0x3a4038,0x3a4040),
(0x39b99e,0x39b9a4),(0x39b9d0,0x39b9d8),(0x39b9ee,0x39b9f8))
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')

def parse_instructions(text):
    found={}
    for line in text.splitlines():
        m=LINE.match(line)
        if m:
            a=int(m[1],16)
            if a in found:raise ValueError('duplicate native instruction')
            found[a]=(m[2].lower(),' '.join(m[3].split('@')[0].split('<')[0].split()))
    return found

def check_pins(insns):
    return [label for label,addr,op,args in PINS if insns.get(addr)!=(op,args)]

def audit(path,objdump='llvm-objdump'):
    path=Path(path)
    if path.stat().st_size!=SIZE or hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:
        raise ValueError('source mismatch')
    command=shutil.which(objdump)
    if not command:raise ValueError('llvm-objdump required')
    insns={}
    for start,stop in BOUNDS:
        p=subprocess.run((command,'--triple=thumbv7a-linux-gnueabihf','--disassemble',
            '--start-address='+hex(start),'--stop-address='+hex(stop),str(path)),
            capture_output=True,text=True,check=True,timeout=10)
        part=parse_instructions(p.stdout)
        if not part or set(part).intersection(insns):raise ValueError('overlap/empty')
        insns.update(part)
    failures=check_pins(insns)
    return {'source':'ORIGINAL_NATIVE_STATIC','checks':len(PINS),
        'passed':len(PINS)-len(failures),'failed':failures,
        'incoming_4013_branch':'PINNED',
        'compression_zero_path':'BYPASSES_LZ4',
        'rx_decrypt_mode':'SESSION_DEPENDENT_NOT_OBSERVED',
        'server_return_envelope':'NOT_VERIFIED',
        'accepted_phone_reply':False,
        'original_executed':False}

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lib',required=True)
    a=p.parse_args()
    try:r=audit(a.lib)
    except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as ex:
        print(json.dumps({'status':'REFUSED','error':type(ex).__name__}));raise SystemExit(2)
    print(json.dumps(r,sort_keys=True,indent=2))
    raise SystemExit(bool(r['failed']))
