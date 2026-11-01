"""R031: bounded original-native static audit for the incoming plaintext RPC boundary.
No networking, execution of game code, raw packets, keys or original binary published.
"""
import hashlib
import re
import shutil
import subprocess
from pathlib import Path

SHA256='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
SIZE=5243704
SPEC = """gather_payload_size|3ab6dc|ldr.w|r2, [r4, #0x738]
gather_header_size|3ab6e0|ldr.w|r3, [r4, #0x734]
gather_frame_length|3ab6e4|add|r3, r2
payload_length|3abf08|ldr.w|r9, [r4, #0x738]
input_base|3abf0c|ldr.w|r3, [r4, #0x708]
input_cursor|3abf10|ldr.w|r2, [r4, #0x710]
header_length|3abf14|ldr.w|r1, [r4, #0x734]
decrypt_flag|3abf4e|ldrb.w|r11, [r4, #0x72c]
payload_cursor_plus_header|3abf52|add.w|r10, r1, r2
payload_cursor_plus_base|3abf56|add|r10, r3
clear_path_branch|3abf60|beq|0x3abfb2
encrypted_path|3abf74|bl|0x3ab31e
copy_destination|3abfde|ldr|r0, [r7]
copy_original_pointer|3abfe0|mov|r1, r10
copy_original_count|3abfe2|ldr.w|r2, [r4, #0x738]
copy_exact_payload|3abfe6|blx|0x193ed8
copied_length|3abfea|ldr.w|r3, [r4, #0x738]
store_copied_length|3abfee|str.w|r3, [r8]
inbound_4013|3a8de4|movw|r3, #0x4013
compression_flag|3a8dec|ldrb.w|r3, [r4, #0x740]
no_compression_branch|3a8df2|beq|0x3a8ed4
peek_pointer|3a8eda|ldr|r3, [r4]
peek_return_pointer|3a8edc|str.w|r3, [r8]
peek_return_length|3a8ee2|str|r3, [r7]
queue_source|3a4fee|ldr|r1, [sp, #0x10]
queue_size|3a4ff0|mov|r2, r8
queue_enqueue|3a4ffe|bl|0x1b397c
reader_dequeue|3a4018|bl|0x1b37c8
reader_assign|3a403c|bl|0x397316
app_input_pointer|39b99a|mov|r1, r6
app_input_length|39b99c|mov|r2, r7
app_read_buffer|39b9a0|bl|0x3c180e
msg_buffer_construct_reader|3c1818|bl|0x3c1510
app_read_rpc_header|39b9d4|blx|r12
tgcp_parse_base_head|3b720e|bl|0x3af4cc
tgcp_parse_extension_head|3b7244|bl|0x3b6a3c
extension_recognizes_4013|3b6a62|movw|r3, #0x4013
extension_compare_4013|3b6a68|cmp|r5, r3
extension_branch_to_datahead|3b6a6a|beq|0x3b6b00
extension_calls_datahead_parser|3b6b14|bl|0x3b6138
datahead_decode_field_number|3b617c|lsrs|r3, r1, #0x4
datahead_switch_four_fields|3b6180|cmp|r3, #0x3
datahead_read_uint8|3b61b6|bl|0x1f4842
datahead_read_nested_route_length|3b61ec|bl|0x1a333e
datahead_parse_nested_route|3b6200|bl|0x3b2422"""
PINS=tuple((label,int(address,16),op,operand)
           for label,address,op,operand in
           (line.split('|',3) for line in SPEC.splitlines()))
WINDOWS=((0x3ab6dc,0x3ab6e8),(0x3abf08,0x3abf1a),
 (0x3abf4e,0x3abf78),(0x3abfde,0x3abff2),
 (0x3a8de4,0x3a8df6),(0x3a8ed8,0x3a8ee6),
 (0x3a4fea,0x3a5002),(0x3a4014,0x3a401e),
 (0x3a4038,0x3a4042),(0x39b998,0x39b9a4),
 (0x3c1814,0x3c181c),(0x39b9d0,0x39b9d8),
 (0x3b7208,0x3b7212),(0x3b7240,0x3b724a),
 (0x3b6a5e,0x3b6a70),(0x3b6b10,0x3b6b1a),
 (0x3b6178,0x3b6184),(0x3b61b2,0x3b61bc),
 (0x3b61e8,0x3b61f2),(0x3b61fc,0x3b6204))
LINE=re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')
def parse_instructions(source):
    found={}
    for line in source.splitlines():
        match=LINE.match(line)
        if match:
            addr=int(match[1],16)
            if addr in found: raise ValueError('duplicate native instruction')
            found[addr]=(match[2].lower(),' '.join(match[3].split('@',1)[0].split('<',1)[0].split()))
    return found
def failures(insns):
    return [name for name,addr,op,args in PINS if insns.get(addr)!=(op,args)]
def audit(path,objdump='llvm-objdump'):
    path=Path(path)
    if path.stat().st_size!=SIZE or hashlib.sha256(path.read_bytes()).hexdigest()!=SHA256:
        raise ValueError('exact owner-provided Apollo required')
    cmd=shutil.which(objdump)
    if not cmd:raise ValueError('llvm-objdump unavailable')
    insns={}
    for start,end in WINDOWS:
        result=subprocess.run([cmd,'--triple=thumbv7a-linux-gnueabihf',
            '--disassemble','--start-address='+hex(start),'--stop-address='+hex(end),
            str(path)],capture_output=True,text=True,check=True,timeout=12)
        part=parse_instructions(result.stdout)
        if not part or set(part).intersection(insns):raise ValueError('bad native window')
        insns.update(part)
    bad=failures(insns)
    return {'source':'ORIGINAL_NATIVE_STATIC','checks':len(PINS),
            'passed':len(PINS)-len(bad),'failed':bad,
            'conditional_payload_preservation':True,'removes_four_byte_prefix':False,
            'plaintext_session_confirmed':False,'server_envelope_verified':False,
            'original_native_execution':False,'phone_response_accepted':False}
if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser()
    parser.add_argument('--lib',required=True)
    args=parser.parse_args()
    try: result=audit(args.lib)
    except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'result':'REFUSED','error':type(exc).__name__}))
        raise SystemExit(2)
    print(json.dumps(result,indent=2))
    raise SystemExit(bool(result['failed']))
