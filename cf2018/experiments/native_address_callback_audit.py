"""R041: hash-pinned, read-only original Apollo QueryAddrInfo callback path audit.

Static instruction checks only. No runtime execution, phone parsing, or authentication.
"""
import hashlib,json,re,shutil,subprocess
from pathlib import Path

APOLLO_SHA256='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
APOLLO_SIZE=5243704
# (description, original Thumb address, mnemonic, operands/call target)
PINS=(
 ('rpc64_pending_lookup',0x39b9f2,'bl','0x39a3c0'),
 ('rpc64_compare_end',0x39b9fa,'cmp','r3, r0'),
 ('rpc64_matched_branch',0x39b9fc,'bne','0x39ba9e'),
 ('response_type_load',0x39ba9e,'ldr','r3, [r5]'),
 ('response_type2_check',0x39baa0,'cmp','r3, #0x2'),
 ('response_type2_branch',0x39baa2,'beq','0x39bae0'),
 ('parse_original_result',0x39bb08,'bl','0x399a98'),
 ('parse_error_check',0x39bb0e,'cbnz','r0, 0x39bb16'),
 ('result_field_load',0x39bb10,'ldr','r3, [r5, #0x4]'),
 ('success_result0_check',0x39bb12,'cmp','r3, #0x0'),
 ('success_branch',0x39bb14,'beq','0x39bb94'),
 ('response_addr_end',0x39bbc0,'ldr','r3, [r5, #0x10]'),
 ('response_addr_iterator',0x39bbc2,'cmp','r8, r3'),
 ('address_is_domain_check',0x39bbee,'bl','0x399214'),
 ('numeric_handling_flag',0x39bc08,'ldrb.w','r3, [r10, #0x7d]'),
 ('numeric_ipv4_string',0x39bc0e,'ldr.w','r0, [r8, #0x4]'),
 ('numeric_ipv4_check',0x39bc12,'bl','0x394434'),
 ('response_addr_empty_branch',0x39bd6a,'bne','0x39bd9c'),
 ('empty_result_callback',0x39bd7e,'bl','0x3997b8'),
 ('empty_result_session_erase',0x39bd90,'bl','0x39a55c'),
 ('empty_result_cache',0x39bd96,'bl','0x39a78c'),
 ('nonempty_response_queue',0x39bdea,'bl','0x39b7ca'),
 ('queue_begin',0x39c16a,'ldr','r4, [r0, #0x68]'),
 ('queue_end',0x39c16e,'ldr','r3, [r0, #0x6c]'),
 ('queued_rpc64_find',0x39c1b4,'bl','0x39a3c0'),
 ('queued_rpc64_compare',0x39c1bc,'cmp','r0, r3'),
 ('queued_addr_iter',0x39c1fc,'ldr','r7, [r4, #0x14]'),
 ('queued_addr_dns',0x39c21c,'bl','0x39b1f8'),
 ('queued_completion_callback',0x39c2c2,'bl','0x3997b8'),
 ('queued_session_erase',0x39c2ca,'bl','0x39a55c'),
 ('queued_addr_cache',0x39c2d0,'bl','0x39a78c'),
 ('update_requests',0x39da0c,'bl','0x39ad50'),
 ('update_timeouts',0x39da16,'bl','0x39af10'),
 ('update_dispatch',0x39da20,'bl','0x39c164'),
)
WINDOWS=(
 (0x39b9f0,0x39ba00),(0x39ba9c,0x39baa6),
 (0x39bb04,0x39bb18),(0x39bbbc,0x39bbc6),
 (0x39bbe8,0x39bbf2),(0x39bc04,0x39bc16),
 (0x39bd66,0x39bd9e),(0x39bde6,0x39bdf0),
 (0x39c168,0x39c174),(0x39c1b0,0x39c1c0),
 (0x39c1fa,0x39c200),(0x39c21a,0x39c222),
 (0x39c2be,0x39c2d4),(0x39da08,0x39da24),
)
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-z][\w.]*)\s*(.*)$')
def parse_instruction_lines(lines):
    out={}
    for line in lines:
        match=LINE.match(line)
        if match:
            addr=int(match.group(1),16)
            if addr in out:raise ValueError('duplicate instruction address')
            operands=match.group(3).split('@')[0].split('<')[0].strip()
            out[addr]=(match.group(2).lower(),' '.join(operands.split()))
    return out
def failures(insns):
    return [name for name,addr,op,operands in PINS if insns.get(addr)!=(op,operands)]
def audit(original_library):
    lib=Path(original_library)
    if lib.stat().st_size!=APOLLO_SIZE or hashlib.sha256(lib.read_bytes()).hexdigest()!=APOLLO_SHA256:
        raise ValueError('exact original Apollo hash/size mismatch')
    objdump=shutil.which('llvm-objdump')
    if not objdump:raise ValueError('llvm-objdump required')
    insns={}
    for start,end in WINDOWS:
        cmd=(objdump,'--triple=thumbv7a-linux-gnueabihf','--disassemble',
             f'--start-address={start:#x}',f'--stop-address={end:#x}',str(lib))
        result=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=15)
        chunk=parse_instruction_lines(result.stdout.splitlines())
        if not chunk or set(insns).intersection(chunk):
            raise ValueError('empty or overlapping disassembly windows')
        insns.update(chunk)
    bad=failures(insns)
    return {
      'evidence':'ORIGINAL_APOLLO_STATIC_ONLY','verified':len(PINS)-len(bad),
      'total':len(PINS),'failures':bad,
      'stage1':'RPC64_FIND -> TYPE2 -> READ -> RESULT0 -> COPY_OR_QUEUE',
      'stage2':'UPDATE -> QUEUED_RESULT -> DNS_IF_NEEDED -> CALLBACK -> ERASE',
      'success_callback_is_unconditional':False,
      'ten_byte_service_name_identified':False,
      'real_phone_callback_observed':False,'game_authenticated':False,
    }
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--lib',required=True)
    args=parser.parse_args()
    try:result=audit(args.lib)
    except (OSError,ValueError,subprocess.TimeoutExpired,subprocess.CalledProcessError) as exc:
        print(json.dumps({'status':'REFUSED','error_type':type(exc).__name__}))
        raise SystemExit(2)
    print(json.dumps(result,indent=2))
    raise SystemExit(bool(result['failures']))
