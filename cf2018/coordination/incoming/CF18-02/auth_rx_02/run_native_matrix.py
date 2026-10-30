"""Explicit offline reproduction; no arguments runs nothing, no network or phone."""
import argparse
import hashlib
import json
from pathlib import Path
from auth_v12_fixtures import EXPECTED, reply
from tgcp_body_envelope import corrected_v12_fixture
from auth_rx_native_controls import trace_wire, trace_component


def _codes(result):
    stages = {}
    for e in result['events']:
        if e['event'] == 'return':
            stages.setdefault(e['stage'], []).append(e['code'])
    return stages


def matrix(library):
    records = []
    for arm in EXPECTED:
        old, new = reply(arm), corrected_v12_fixture(arm)
        original = trace_wire(library, old)
        corrected = trace_wire(library, new)
        auth = old[49:]  # pinned union begins at 42 and has seven-byte tag/length
        isolated_auth = trace_component(library, auth, component='auth')
        isolated_account = None
        if auth:
            count = int.from_bytes(auth[1:5], 'big')
            isolated_account = trace_component(library, auth[5:5+count], component='account')
        records.append({'arm': arm,
            'original': {'length': len(old), 'sha256': hashlib.sha256(old).hexdigest(),
                'native_codes': _codes(original), 'effective_type': original['effective_type'],
                'header_length': original['header_length'], 'body_length': original['body_length'],
                'predicates': original['predicates'], 'state': original['state'],
                'account_unchanged': original['account_unchanged'], 'stubs': sorted(set(original['stubs']))},
            'isolated_components_not_reached_on_original_path': {
                'auth_return': isolated_auth['return'], 'auth_consumed': isolated_auth['consumed'],
                'account_return': None if isolated_account is None else isolated_account['return'],
                'account_consumed': None if isolated_account is None else isolated_account['consumed']},
            'corrected': {'length': len(new), 'sha256': hashlib.sha256(new).hexdigest(),
                'native_codes': _codes(corrected), 'effective_type': corrected['effective_type'],
                'header_length': corrected['header_length'], 'body_length': corrected['body_length'],
                'predicates': corrected['predicates'], 'state': corrected['state'],
                'synthetic_uid_zero': corrected['synthetic_uid_zero'], 'stubs': sorted(set(corrected['stubs']))}})
    return {'schema': 1, 'source_sha256': hashlib.sha256(Path(library).read_bytes()).hexdigest(),
            'evidence': 'PINNED_NATIVE_EMULATION_WITH_STUBS; SYNTHETIC_RESPONSES; NOT_PHONE_AUTH',
            'context': 'Fresh initialized state 3, zero method/key, synthetic prior account; complete preloaded input; net wrapper -3.',
            'records': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library')
    args = parser.parse_args()
    if not args.library:
        print('Inactive: supply --library for explicit private-source offline validation.')
    else:
        print(json.dumps(matrix(args.library), indent=2))
