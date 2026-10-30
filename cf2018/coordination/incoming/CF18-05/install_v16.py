"""Build v1.6 add-on *locally* from the exact, already installed v1.5 script.

No original/captured SYN fixtures or proprietary APK contents are downloaded,
modified or published. No sockets, background jobs or device run.
"""
import hashlib
from pathlib import Path

PIN = 'abfb6e46c54f71beb60769c4e6ca1221cccefbd9d72cecd902eb91cc59632f46'
OUTPUT = '054ded025008667df931c34495f29999b1805d12529250057caf9e91a5e1fbb2'
START_SHA = '4b00d396ca0d438e1930dfcffd6d9a5351477eadcb4d05d9a2b909756223126d'


def generate(root):
    root = Path(root)
    src = root / 'stage_probe_v15.py'
    source = src.read_bytes()
    if hashlib.sha256(source).hexdigest() != PIN:
        raise ValueError('v1.5 source pin mismatch; refusing an unsafe text patch')
    if not (root / 'route_fingerprint_v16.py').is_file():
        raise FileNotFoundError('download route_fingerprint_v16.py first')
    s = source.decode('utf-8')
    substitutions = [
        ('"""Bounded v1.5 post-auth Bingo/WAIT stage comparison (six connections).', '"""Bounded v1.6 post-Bingo routed-RPC fingerprint (two connections).'),
        ('from stage_frame_v15 import ARMS, candidate_stage', 'from stage_frame_v15 import candidate_stage\nfrom route_fingerprint_v16 import inspect_routed_frame'),
        ('MAX_SLOTS=6', 'MAX_SLOTS=2'),
        ('arm=ARMS[(slot-1)%len(ARMS)]', "arm='CORRECTED_BINGO_SYNTHETIC'"),
        ('inp=inp[used:];frames+=1', 'wire_frame=inp[:used];inp=inp[used:];frames+=1'),
        ("run.record('later_client_frame',cid,slot=slot,variant=kind,frame_bytes=frame['frame_bytes'],header_bytes=frame['header_bytes'],body_bytes=frame['body_bytes'],frame_digest=frame['sha256'],after_last_reply_ms=elapsed)",
         "run.record('later_client_frame',cid,slot=slot,variant=kind,frame_bytes=frame['frame_bytes'],header_bytes=frame['header_bytes'],body_bytes=frame['body_bytes'],after_last_reply_ms=elapsed)\n                        if sel == [[0x4013,1]]:\n                            run.record('routed_rpc_hint',cid,slot=slot,**inspect_routed_frame(wire_frame,frame))"),
        ("if frames>=4:status='frame_cap';break", "if frames>=3:status='routed_frame_seen';break"),
        ('CF2018 v1.5 — corrected auth 0x2002 then WAIT/Bingo synthetic stage comparison', 'CF2018 v1.6 — post-Bingo 0x4013 privacy-safe RPC fingerprint'),
        ('Arms: CORRECTED_ONLY; CORRECTED_WAIT; CORRECTED_BINGO_SYNTHETIC. All synthetic.', 'Two repetitions: CORRECTED_BINGO_SYNTHETIC only. No raw packet stored.'),
        ('    # Summarize proxy lifecycle metadata only; never include raw payload/IP/credentials.',
         "    hints=[e for e in ev if e['action']=='routed_rpc_hint']\n    for h in hints:\n        out.append('ROUTED_HINT slot={} type={} frame={} header={} body={} envelope={} method={} offset={} rpc_type={} confidence={}'.format(\n            h['slot'],h['route_type'],h['frame_bytes'],h['header_bytes'],h['body_bytes'],\n            h['body_envelope_hint'],h['rpc_hint'],h['rpc_offset'],h['rpc_type_hint'],h['rpc_confidence']))\n    # Summarize proxy lifecycle metadata only; never include raw payload/IP/credentials."),
        ("out+=['','DISCLAIMERS: all packets are synthetic; WAIT and Bingo do not create real accounts/sessions.',",
         "out+=['','HINT ONLY: an allowlisted name signature is not decoded RPC proof; opaque does not prove encryption.',\n          'DISCLAIMERS: server packets are synthetic; this does not create real accounts/sessions.',"),
        ('Offline only. Set CF2018_V15_LIVE=YES for exactly six sessions.', 'Offline only. Set CF2018_V16_LIVE=YES for exactly two sessions.'),
        ('CF2018 v1.5: 6 sessions, CORRECTED_ONLY / CORRECTED_WAIT / CORRECTED_BINGO_SYNTHETIC, twice.', 'CF2018 v1.6: 2 Bingo-only sessions, 0x4013 structural method hint, no payload storage.'),
        ('CF2018_v15_Bingo_Stage_Result.txt', 'CF2018_v16_Routed_Fingerprint_Result.txt'),
        ('cf2018_v15_runs', 'cf2018_v16_runs'),
        (' after_last_reply_ms={e["after_last_reply_ms"]} sha256={e["frame_digest"]}',
         ' after_last_reply_ms={e["after_last_reply_ms"]}'),
    ]
    for old, new in substitutions:
        if s.count(old) != 1:
            raise ValueError('v1.5 anchor mismatch: ' + old[:60])
        s = s.replace(old, new)
    if hashlib.sha256(s.encode()).hexdigest() != OUTPUT:
        raise ValueError('generated v1.6 hash mismatch')
    start = '#!/data/data/com.termux/files/usr/bin/bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\npython -m unittest discover -s tests -p \'test_v16_route.py\' -v\nif [[ "${CF2018_V16_LIVE:-NO}" != \'YES\' ]]; then\n    echo \'Offline checks finished. To run exactly 2 local Bingo sessions: CF2018_V16_LIVE=YES bash START_V16.sh\'\n    exit 0\nfi\npython route_probe_v16.py --live-opt-in\n'
    if hashlib.sha256(start.encode()).hexdigest() != START_SHA:
        raise ValueError('startup hash mismatch')
    (root / 'route_probe_v16.py').write_text(s)
    (root / 'START_V16.sh').write_text(start)
    print('Generated route_probe_v16.py and START_V16.sh; v1.5 unchanged.')


if __name__ == '__main__':
    generate(Path(__file__).resolve().parent)
