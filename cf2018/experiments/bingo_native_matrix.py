"""Explicit private-source offline reproduction. No args means inactive."""
import argparse
import hashlib
import json
from pathlib import Path
from native_bingo_controls import (component_probe, decoded_probe, mismatched_auth_wire,
                            relay_reuse_prefix, wire_probe)


def matrix(library):
    records = []
    def add(name, result):
        records.append({'control': name, 'actual': result})
    add('no_data_bingo', wire_probe(library))
    add('no_data_ready_handler', wire_probe(library, ready=True))
    add('EOF_like_status_ready_handler', wire_probe(library, ready=True, network_result=-4))
    for header in (0x3002, 0x6002):
        wire = mismatched_auth_wire(header)
        result = wire_probe(library, wire)
        result.update(negative_fixture_length=len(wire),
                      negative_fixture_sha256=hashlib.sha256(wire).hexdigest())
        add(f'INVALID_header_{header:04x}_auth_union_2002', result)
    add('decoded_wrong_header_before_body', decoded_probe(library, header_type=0x2002))
    add('decoded_receive_real_truncated_body', decoded_probe(library))
    add('decoded_receive_parser_failure_STUB', decoded_probe(library, parser_result=-32))
    add('queue_copy_parser_zero_STUB', decoded_probe(library, header_type=0x3002, parser_result=0))
    add('relay_copy_parser_zero_STUB', decoded_probe(library, parser_result=0))
    add('selector_replaced_with_wait_STUB', decoded_probe(library, parser_result=0, decoded_selector=0x3002))
    for code in (-12, -10, -31):
        add(f'decoded_receive_error_{code}_STUB', decoded_probe(library, receive_result=code))
    for name, payload, component, declared in [
        ('empty_bingo', b'', 'bingo', None),
        ('empty_relay', b'', 'relay', None),
        ('empty_nested_relay', b'\x15\0\0\0\0', 'bingo', None),
        ('compression_without_relay', b'\x21\x03\x31\x80\x20', 'bingo', None),
        ('zero_identity_length', b'\x25\0\0\0\0', 'relay', None),
        ('declared_overrun', b'\x11\x01', 'relay', 1),
        ('physical_truncation', b'\x11\x80', 'relay', None),
        ('exact_17_Z_identity', b'\x25\0\0\0\x11'+b'Z'*17, 'relay', None),
    ]:
        add(name, component_probe(library, payload, component=component, declared=declared))
    add('relay_reuse_SYN_prefix_stop_before_send', relay_reuse_prefix(library))
    return {'schema': 1,
            'library_sha256': hashlib.sha256(Path(library).read_bytes()).hexdigest(),
            'evidence': 'NATIVE_WITH_EXPLICIT_STUBS; SYNTHETIC_NEGATIVES; NO_VALID_BINGO_OR_PHONE_AUTH',
            'base_main': 'ccdd219f9ed121e77fc06ad20b50b77614079cbf',
            'records': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library')
    args = parser.parse_args()
    if args.library:
        print(json.dumps(matrix(args.library), indent=2))
    else:
        print('Inactive: supply --library for explicit offline native controls.')
