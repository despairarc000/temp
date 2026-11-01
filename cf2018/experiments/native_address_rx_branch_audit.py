"""Hash-gated, read-only original ARM address-receiver branch audit.

Checks native instruction addresses, not native execution or phone acceptance.
Exports only fixed labels; never prints original disassembly or packet bytes.
"""
import hashlib
import re
import shutil
import subprocess
from pathlib import Path

SOURCE_SHA = '4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
PINS = {
    'header_read': (0x39b9d4, 'blx', 'r12'),
    'pending_find': (0x39b9f2, 'bl', '0x39a3c0'),
    'pending_test': (0x39b9fa, 'cmp', 'r3, r0'),
    'found_session_branch': (0x39b9fc, 'bne', '0x39ba9e'),
    'type_two_check': (0x39baa0, 'cmp', 'r3, #0x2'),
    'type_two_branch': (0x39baa2, 'beq', '0x39bae0'),
    'typed_reader': (0x39bb08, 'bl', '0x399a98'),
    'generated_result_reader': (0x399ac8, 'bl', '0x39eebc'),
    'address_begin_end_compare': (0x39bd5e, 'cmp', 'r3, r7'),
    'different_address_branch': (0x39bd6a, 'bne', '0x39bd9c'),
    'empty_address_callback': (0x39bd7e, 'bl', '0x3997b8'),
    'empty_address_erase': (0x39bd90, 'bl', '0x39a55c'),
    'empty_address_cache': (0x39bd96, 'bl', '0x39a78c'),
    'nonempty_record_construct': (0x39bda2, 'bl', '0x2013ae'),
    'nonempty_enqueue': (0x39bdea, 'bl', '0x39b7ca'),
}
WINDOWS = (
    (0x39b9ce,0x39ba08), (0x39ba98,0x39bab6),
    (0x39bb00,0x39bb18), (0x39bd56,0x39bdaa),
    (0x39bde0,0x39bdfa), (0x399ac4,0x399ad0)
)
LINE = re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')


def parse_lines(output):
    parsed = {}
    for line in output.splitlines():
        match = LINE.match(line)
        if match:
            parsed[int(match[1], 16)] = (
                match[2].lower(),
                ' '.join(match[3].split('@',1)[0].split('<',1)[0].strip().split())
            )
    return parsed


def compare(insns):
    return [label for label, (address, name, args) in PINS.items()
            if insns.get(address) != (name, args)]


def audit(path):
    path = Path(path)
    if path.stat().st_size != 5243704:
        raise ValueError('wrong native source size')
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('wrong native source hash')
    tool = shutil.which('llvm-objdump')
    if not tool:
        raise ValueError('llvm-objdump required')
    insns = {}
    for start, end in WINDOWS:
        result = subprocess.run([
            tool, '--triple=thumbv7a-linux-gnueabihf', '--disassemble',
            '--start-address=' + hex(start), '--stop-address=' + hex(end), str(path)
        ], capture_output=True, text=True, check=True, timeout=12)
        part = parse_lines(result.stdout)
        if set(insns).intersection(part):
            raise ValueError('overlapping native windows')
        insns.update(part)
    failed = compare(insns)
    return {
        'verified_original': True, 'checks': len(PINS),
        'passed': len(PINS) - len(failed), 'failed': failed,
        'native_executed': False, 'client_accepted_reply': False,
        'findings': [
            'rpc64_pending_query_session_lookup',
            'type2_typed_decoder',
            'empty_vs_nonempty_processed_address_paths'
        ]
    }
