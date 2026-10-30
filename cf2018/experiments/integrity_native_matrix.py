"""Opt-in read-only integrity investigation. No patch, image decoding or phone run."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
from native_integrity_controls import (PINS, classify_branch, native_crc,
                                      postload_comparison, mono_handoff)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from managed_image_preflight import inspect_image


def matrix(tprt, mono, apk):
    path=Path(apk)
    if path.stat().st_size != 30884905 or hashlib.sha256(path.read_bytes()).hexdigest() != '33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9':
        raise ValueError('unexpected private APK fingerprint')
    images=[]
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            if name.startswith('assets/bin/Data/Managed/') and name.endswith('.dll'):
                images.append({'member':name,'preflight':inspect_image(z.read(name))})
    branches=[{'name':name,'actual':classify_branch(tprt,prefix,length)}
              for name,prefix,length in [('opaque',b'ABCD',8192),('MZ_branch',b'MZ00',8192),
                                         ('TXP_small',b'TXP0',4096),('TXP_large',b'TXP0',8192)]]
    comparisons=[{'before':a,'supplied_lookup':b,'actual':postload_comparison(tprt,a,b)}
                 for a,b in ((123,123),(123,124),(0,124),(123,0))]
    return {'schema':1,'base_main':'6a0ecc16877adbdc4eed03cefebb5b4144f7bd6f',
            'library_pins':{k:list(v) for k,v in PINS.items()},
            'images':images,'mono_handoff':mono_handoff(mono,tprt),
            'synthetic_signature_controls':branches,
            'native_crc_standard_vector':native_crc(tprt,b'123456789'),
            'injected_postload_controls':comparisons,
            'phone_exit_cause':'NOT_ESTABLISHED',
            'safe_modified_build':'NOT_ESTABLISHED',
            'original_files_modified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('tprt','mono','apk'):p.add_argument('--'+name)
    a=p.parse_args()
    if all((a.tprt,a.mono,a.apk)):
        print(json.dumps(matrix(a.tprt,a.mono,a.apk),indent=2))
    else:print('Inactive: supply explicit --tprt --mono --apk private paths for read-only analysis.')
