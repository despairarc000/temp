"""Hash-pinned read-only original CF2018 incoming application-byte chain.

No network, game execution, payloads, account data, keys or emulation.
The call chain is conditional and does not prove server return framing.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import re
import shutil
import subprocess

SHA256 = '4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
SOURCE_BYTES = 5243704
PINS = (
    ('peek_invokes_receive_unpack', 0x3a8d6e, 'bl', '0x3abe34'),
    ('ingress_calls_peek', 0x3a4f4c, 'bl', '0x3a8c4c'),
    ('ingress_queues_bytes', 0x3a4ffe, 'bl', '0x1b397c'),
    ('tgcp_read_dequeues_bytes', 0x3a4018, 'bl', '0x1b37c8'),
    ('tgcp_read_assigns_bytes', 0x3a403c, 'bl', '0x397316'),
    ('connector_read_calls_tgcp_read', 0x3c5bf0, 'bl', '0x3a3f88'),
    ('connector_receive_schedules_callback', 0x3c5e86, 'bl', '0x381cda'),
    ('connector_dispatches_observer', 0x3c651e, 'blx', 'r9'),
    ('address_receives_via_connector', 0x39d4d4, 'blx', 'r12'),
    ('address_gets_input_data', 0x39d546, 'bl', '0x3972f8'),
    ('address_gets_input_size', 0x39d54e, 'bl', '0x3972f0'),
    ('address_calls_process_response', 0x39d558, 'bl', '0x39b90c'),
    ('response_reads_message_header', 0x39b9d4, 'blx', 'r12'),
    ('response_finds_rpc64_session', 0x39b9f2, 'bl', '0x39a3c0'),
    ('response_requires_type_two', 0x39baa0, 'cmp', 'r3, #0x2'),
    ('response_dispatches_address_decoder', 0x39bb08, 'bl', '0x399a98'),
)
WINDOWS = ((0x3a8d64,0x3a8d78), (0x3a4f42,0x3a5005),
           (0x3a4012,0x3a4042), (0x3c5be4,0x3c5c08),
           (0x3c5e7a,0x3c5e8c), (0x3c650c,0x3c6520),
           (0x39d4ca,0x39d55c), (0x39b9ca,0x39ba00),
           (0x39ba9e,0x39baa4), (0x39bb04,0x39bb0c))
LINE = re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')

def parse_instructions(source):
    result = {}
    for line in source.splitlines():
        m = LINE.match(line)
        if m:
            address = int(m[1], 16)
            if address in result:
                raise ValueError('duplicate disassembly address')
            result[address] = (m[2].lower(),
                               ' '.join(m[3].split('@', 1)[0].split('<', 1)[0].split()))
    return result

def compare(insns):
    return [name for name, addr, op, operand in PINS
            if insns.get(addr) != (op, operand)]

def audit(lib, tool='llvm-objdump'):
    path = Path(lib)
    if path.stat().st_size != SOURCE_BYTES or hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError('source is not exact original Apollo')
    executable = shutil.which(tool)
    if not executable:
        raise ValueError('llvm-objdump is unavailable')
    inspected = {}
    for start, end in WINDOWS:
        p = subprocess.run([executable, '--triple=thumbv7a-linux-gnueabihf',
            '--disassemble', '--start-address=' + hex(start), '--stop-address=' + hex(end),
            str(path)], capture_output=True, text=True, check=True, timeout=10)
        part = parse_instructions(p.stdout)
        if not part or set(part).intersection(inspected):
            raise ValueError('ambiguous or overlapping original windows')
        inspected.update(part)
    failed = compare(inspected)
    return {'verified_original': True, 'checks': len(PINS),
            'passed': len(PINS)-len(failed), 'failed': failed,
            'source': 'ORIGINAL_NATIVE_STATIC',
            'incoming_application_byte_chain': 'PINNED',
            'server_return_framing': 'NOT_VERIFIED',
            'live_response_sent': False, 'client_response_accepted': False}

if __name__ == '__main__':
    import argparse, json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', required=True)
    args = parser.parse_args()
    try:
        result = audit(args.lib)
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'result':'REFUSED', 'error_type': type(exc).__name__}))
        raise SystemExit(2)
    print(json.dumps(result, sort_keys=True, indent=2))
    raise SystemExit(0 if not result['failed'] else 1)
