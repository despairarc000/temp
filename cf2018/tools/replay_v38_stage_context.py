"""Opt-in private-source native stage replay and native/parser differential.

No socket, no original modification; metadata only. Source ZIP not redistributed.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from native_control import NativeControl,CTX,BUF
from native_rpc_header import binary_header

def replay(library,source):
    source=Path(source).resolve()
    pins=json.loads((ROOT/'coordination/V38_SOURCE_PINS.json').read_text())
    for name,digest in pins.items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('private source mismatch: '+name)
    sys.path.insert(0,str(source))
    from ack_wire import make_candidate_ack
    from preflight_v09 import strict_header_candidate
    from tgcp_body_repair_v14 import candidate
    from stage_frame_v15 import candidate_stage
    from legacy_thrift_v37 import classify_legacy_thrift
    syn=bytes.fromhex((source/'golden_request.hex').read_text().strip())
    if len(syn)!=133:raise ValueError('unexpected private routing fixture size')
    frames=[('ack',strict_header_candidate(make_candidate_ack(syn)),0x3ac0b8),
            ('auth',candidate('V14_BODY_ENVELOPED'),0x3ac306),
            ('bingo',candidate_stage('CORRECTED_BINGO_SYNTHETIC'),0x3ac39e)]
    saved=None;stages=[]
    for name,wire,entry in frames:
        n=NativeControl(library)
        if saved is not None:n.uc.mem_write(CTX,saved)
        if name=='ack':n.write(CTX+4,42);n.write(CTX+0x11c,4)
        if name=='auth':n.write(CTX+0x6c8,3) # explicit auth-send transition omitted
        n.write(CTX+0x708,BUF);n.write(CTX+0x70c,65536)
        n.write(CTX+0x710,0);n.write(CTX+0x714,len(wire));n.uc.mem_write(BUF,wire)
        result=n.execute(entry,(CTX,0),{0x284fcc:('no-data boundary; no socket',-3)})
        stages.append({'stage':name,'wire_length':len(wire),'return':result,
                       'crypto_method':n.read(CTX+0x11c),'key_mode':n.read(CTX+0x120),
                       'key_present':bool(n.read(CTX+0x458,1)),
                       'state':n.read(CTX+0x6c8),'compression':n.read(CTX+0x33f4),
                       'stubs':n.calls})
        saved=bytes(n.uc.mem_read(CTX,0x40000))
    differential=[]
    for strict in (False,True):
        result=binary_header(library,strict=strict)
        classified=classify_legacy_thrift(bytes(4)+result['wire']+b'\0')
        differential.append({'native_strict':strict,'native_header_length':len(result['wire']),
                             'classifier':classified})
    return {'source_zip_sha256':'e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2',
            'stages':stages,'differential':differential,
            'limits':['fresh ELF per stage, fixed-address context snapshot carried forward',
                      'state3 explicitly supplied; actual auth send omitted',
                      'no-data wrapper and bounded memory/log helpers substituted',
                      'synthetic lab stages, not accepted real account or Android call trace',
                      'transport write sink substituted only for native header differential']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library');p.add_argument('--source');a=p.parse_args()
    if a.library and a.source:print(json.dumps(replay(a.library,a.source),indent=2))
    else:print('Inactive: explicit --library and private --source directory required.')
