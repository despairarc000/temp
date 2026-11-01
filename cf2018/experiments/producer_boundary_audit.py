"""Read-only pinned original CF2018 application TX-boundary audit.

Python standard library + optional llvm-objdump; outputs only fixed labels.
Does not send packets, modify game files, or print disassembly/private paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

EXPECTED_BYTES = 5243704
EXPECTED_SHA256 = '4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
BOUNDS = (
    (0x3998d4, 0x3999ac),
    (0x39ad50, 0x39ae50),
    (0x39cb64, 0x39cb76),  # AddressService connection binding
    (0x3c2930, 0x3c2942),  # RpcConnector connection binding
    (0x3c18ec, 0x3c1946),
    (0x3c1ed0, 0x3c1f68),
    (0x3c5fd0, 0x3c6055),
    (0x3a4708, 0x3a47e8),
    (0x3a53d0, 0x3a5480),
    (0x397316, 0x39731c),  # AString assign delegation
    (0x396080, 0x3960a2),  # AData assign: clear and append
    (0x395fc4, 0x396004),  # AData append: memory copy
    (0x39d4a4, 0x39d565),  # AddressService receive callback
    (0x39c1a8, 0x39c1d0),  # AddressService response session lookup
    (0x3c4ee4, 0x3c4f40),  # RpcConnector receive callback
    (0x3c3ab0, 0x3c3bac),  # RpcConnector message dispatch
)
# Source-relative instruction checks; no original disassembly/payload is published.
PINS = (
    ('request_invokes_QueryAddrInfo', 0x39ae3c, 'bl', '0x3998d4'),
    ('QueryAddrInfo_calls_args_writer', 0x39991c, 'bl', '0x39ed4c'),
    ('QueryAddrInfo_calls_virtual_message_begin', 0x399904, 'blx', 'r3'),
    ('QueryAddrInfo_calls_virtual_message_end', 0x399926, 'blx', 'r3'),
    ('QueryAddrInfo_calls_virtual_protocol_helper', 0x399936, 'blx', 'r3'),
    ('QueryAddrInfo_calls_inner_virtual_method', 0x399958, 'blx', 'r10'),
    ('QueryAddrInfo_calls_second_inner_virtual', 0x39997e, 'blx', 'r3'),
    ('QueryAddrInfo_calls_third_inner_virtual', 0x39999a, 'blx', 'r3'),
    ('address_service_connect_binds_msgbuffer', 0x39cb68, 'bl', '0x3c18ec'),
    ('rpc_connector_connect_binds_msgbuffer', 0x3c2934, 'bl', '0x3c18ec'),
    ('msg_buffer_bind_captures_connector', 0x3c191e, 'str', '[r0, #0xc]'),
    ('msg_buffer_bind_stores_callback', 0x3c193e, 'str', '[r4, #0x50]'),
    ('write_end_reads_first_buffer_pointer', 0x3c1ee0, 'ldr.w', '[r0, #0x4]'),
    ('write_end_reads_end_buffer_pointer', 0x3c1ee4, 'ldr.w', '[r0, #0xc]'),
    ('write_end_fetches_virtual_dispatch', 0x3c1f0c, 'ldr', '[r4]'),
    ('write_end_calls_virtual_dispatch', 0x3c1f12, 'blx', 'r3'),
    ('write_end_loads_bound_callback', 0x3c1f3c, 'ldr.w', '[r4, #0x50]'),
    ('write_end_invokes_bound_callback', 0x3c1f46, 'blx', 'r12'),
    ('connector_checks_length_ceiling', 0x3c5ff2, 'cmp', 'r7, r3'),
    ('connector_copies_passed_bytes', 0x3c601e, 'bl', '0x397316'),
    ('connector_checks_tgcp_pointer', 0x3c6022, 'ldr.w', '[r6, #0x198]'),
    ('connector_checks_connection', 0x3c6028, 'bl', '0x3a37e4'),
    ('connector_invokes_route_write', 0x3c6046, 'bl', '0x3a4708'),
    ('route_write_enqueues', 0x3a47dc, 'bl', '0x3a4594'),
    ('queue_pop', 0x3a53e0, 'bl', '0x3a43ac'),
    ('queued_routed_send', 0x3a5476, 'bl', '0x3a91ec'),
    ('msg_buffer_computes_exact_length', 0x3c1eec, 'rsb', 'r6, r11, r10'),
    ('msg_buffer_forwards_existing_pointer', 0x3c1f42, 'mov', 'r2, r11'),
    ('msg_buffer_forwards_existing_length', 0x3c1f44, 'mov', 'r3, r6'),
    ('connector_forwards_source_ptr_to_assign', 0x3c601a, 'mov', 'r1, r8'),
    ('connector_forwards_source_len_to_assign', 0x3c601c, 'mov', 'r2, r7'),
    ('astring_assign_dispatches_adata_assign', 0x397318, 'b.w', '0x396080'),
    ('adata_assign_clears_previous_bytes', 0x396088, 'bl', '0x39605e'),
    ('adata_assign_dispatches_append', 0x39609c, 'b.w', '0x395fc4'),
    ('adata_append_passes_exact_length', 0x395ff4, 'mov', 'r2, r5'),
    ('adata_append_calls_memcpy', 0x395ffa, 'blx', '0x193ed8'),
    ('address_receive_virtual_read', 0x39d4d4, 'blx', 'r12'),
    ('address_receive_calls_response_parser', 0x39d558, 'bl', '0x39b90c'),
    ('address_response_looks_up_session', 0x39c1b4, 'bl', '0x39a3c0'),
    ('rpc_receive_virtual_read', 0x3c4f14, 'blx', 'r3'),
    ('rpc_receive_calls_message_parser', 0x3c4f2e, 'bl', '0x3c3a24'),
    ('rpc_message_populates_input_buffer', 0x3c3ab8, 'bl', '0x3c180e'),
    ('rpc_message_dispatches_response', 0x3c3ba0, 'bl', '0x3c382c'),
)
LINE = re.compile(r'^\s*([0-9a-fA-F]{6,8}):\s+(?:[0-9a-fA-F]{4}\s+){1,2}([a-zA-Z.][\w.]*)\s*(.*)$')


def parse_instructions(output: str) -> dict[int, tuple[str, str]]:
    result = {}
    for line in output.splitlines():
        m = LINE.match(line)
        if m:
            address = int(m.group(1), 16)
            operands = m.group(3).split('@', 1)[0].split('<', 1)[0].strip()
            if address in result:
                raise ValueError('duplicate instruction address')
            result[address] = m.group(2).lower(), ' '.join(operands.split())
    return result


def audit_instructions(insns: dict[int, tuple[str, str]]) -> tuple[list[str], list[str]]:
    passed, failed = [], []
    for label, addr, mnemonic, operand in PINS:
        instruction = insns.get(addr)
        if instruction is not None and instruction[0] == mnemonic and (
                instruction[1] == operand if operand.startswith('r') else
                instruction[1].split(' ', 1)[0] == operand if operand.startswith('0x') else
                operand in instruction[1]):
            passed.append(label)
        else:
            failed.append(label)
    return passed, failed


def verify_original(path: Path) -> None:
    if path.stat().st_size != EXPECTED_BYTES:
        raise ValueError('source size mismatch')
    h = hashlib.sha256()
    with path.open('rb') as f:
        head = f.read(52)
        if not (len(head) == 52 and head[:4] == b'\x7fELF' and head[4] == 1
                and head[5] == 1 and struct.unpack_from('<H', head, 18)[0] == 40):
            raise ValueError('source must be ELF32 little-endian ARM')
        h.update(head)
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    if h.hexdigest() != EXPECTED_SHA256:
        raise ValueError('source SHA-256 mismatch')


def audit(path: Path, objdump: str = 'llvm-objdump') -> dict:
    verify_original(path)
    resolved = shutil.which(objdump)
    if not resolved:
        raise ValueError('LLVM llvm-objdump tool not found')
    instructions = {}
    for start, end in BOUNDS:
        result = subprocess.run([resolved, '--triple=thumbv7a-linux-gnueabihf',
                                 '--disassemble', '--start-address='+hex(start),
                                 '--stop-address='+hex(end), str(path)],
                                text=True, capture_output=True, timeout=10,
                                check=True)
        insns = parse_instructions(result.stdout)
        if not insns:
            raise ValueError('empty bounded instruction region')
        if set(instructions).intersection(insns):
            raise ValueError('overlapping bounded instruction regions')
        instructions.update(insns)
    passed, failed = audit_instructions(instructions)
    return {'source': 'PINNED_ORIGINAL_APOLLO_STATIC', 'checks': len(PINS),
            'passed': len(passed), 'failed': failed,
            'verified_source_hash': True, 'native_execution': False,
            'runtime_producer_identified': False,
            'boundaries': ['generated_protocol_virtuals', 'two_connection_binding_callers',
                           'msgbuffer_bound_callback', 'exact_pointer_length_passthrough',
                           'adata_copy_to_memcpy',
                           'connector_size_and_connection_gates', 'routed_tgcp_queue',
                           'address_session_response_dispatch', 'rpc_general_response_dispatch'],
            'phone_test': False, 'gameplay': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', type=Path, required=True)
    parser.add_argument('--objdump', default='llvm-objdump')
    a = parser.parse_args(argv)
    try:
        result = audit(a.lib, a.objdump)
    except (OSError, ValueError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        print(json.dumps({'result': 'REFUSED', 'reason': type(exc).__name__}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if not result['failed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
