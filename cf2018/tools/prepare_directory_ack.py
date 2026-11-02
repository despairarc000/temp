"""Copy-only optional one-ACK experiment from exact R077. No listener starts here.

The owner must explicitly run the prepared probe. It reuses its existing ACK;
no supplied-key reply or next-service auth response is introduced.
"""
import argparse
import hashlib
import os
import shutil
from pathlib import Path
R077_SHA='7cf88b9e011960f334d5eb1a627e04946e27dfae2a5e5bed568b1d449cc6410d'
GATE_SHA='9f7ee1969541ca27a1da48a4f91d4edab89d726383c71513efbe6e357072a43e'
OLD="if (assessment == 'MATCH_EXCEPT_ROUTE' and\n                            False):"
NEW="if (directory_context_matches(raw_frame, original, _R077_ORIGINAL_ROUTE) and\n                            __import__('os').environ.get('CF2018_DIRECTORY_ACK') == 'YES'):"
def directory_context_matches(candidate,reference,original_route):
    """Exact original route + only same-width unit field5 and route14 may differ."""
    from second_service_syn_gate import _parts
    from r056_second_service_syn import first_syn_decision
    try:
        if type(candidate) is not bytes or type(reference) is not bytes or type(original_route) is not bytes:return False
        if len(candidate)!=131 or len(reference)!=133 or len(original_route)!=10:return False
        if first_syn_decision(candidate)[0]!='TEN_BYTE_NAMED_ROUTE_CANDIDATE':return False
        if first_syn_decision(reference)[0]!='REFERENCE_NAMED_ROUTE_CANDIDATE':return False
        a,ae,sa,ra,na=_parts(reference);b,be,sb,rb,nb=_parts(candidate)
        if nb!=original_route or len(na)!=12 or ra[4]!=rb[4]:return False
        if a[0][3]!=b[0][3] or [f[4] for f in a]!=[f[4] for f in b] or ae[0][4]!=be[0][4]:return False
        if [(f[0],f[1],f[4]) for f in sa]!=[(f[0],f[1],f[4]) for f in sb]:return False
        if any(x[3]!=y[3] for x,y in zip(sa,sb) if x[0] not in (5,14)):return False
        x=next(f for f in sa if f[0]==5);y=next(f for f in sb if f[0]==5)
        return x[1]==y[1]==0 and len(x[3])==len(y[3]) and x[2]!=y[2]
    except (ValueError,TypeError,IndexError,StopIteration,OverflowError):return False

def patch(text):
    if hashlib.sha256(text.encode()).hexdigest()!=R077_SHA:raise ValueError('exact prepared R077 handler required')
    if text.count(OLD)!=1:raise ValueError('disabled original ACK anchor required')
    text=text.replace(OLD,NEW,1)
    anchor="from pathlib import Path\n"
    if text.count(anchor)!=1:raise ValueError('original import anchor required')
    text=text.replace(anchor,anchor+'from directory_ack_gate import directory_context_matches\n',1)
    text=text.replace('CF2018_R077_ROUTE_ID_Result.txt','CF2018_DIRECTORY_ACK_Result.txt').replace('cf2018_r077_route_id_runs','cf2018_directory_ack_runs')
    text=text.replace('CF2018 R077 original route equality only; second-service ACK disabled','CF2018 directory one-ACK control; explicit opt-in; not login')
    compile(text,'prepared directory ACK probe','exec')
    return text

def prepare(source,output):
    source=Path(source).resolve();output=Path(output).resolve()
    if output.exists() or output==source or source in output.parents:raise ValueError('new separate output directory required')
    if any(p.is_symlink() for p in source.rglob('*')):raise ValueError('source symlinks refused')
    handler=patch((source/'routed_probe_r037.py').read_text())
    if hashlib.sha256((source/'second_service_syn_gate.py').read_bytes()).hexdigest()!=GATE_SHA:raise ValueError('original SYN parser required')
    for name in ('r076_private_route_equality.py','r075_directory_connector_discriminator.py','r057_original_address_callers.py','r058_name_service_wiring.py'):
        if not (source/name).is_file():raise ValueError('complete R077 source required')
    shutil.copytree(source,output)
    (output/'routed_probe_r037.py').write_text(handler)
    (output/'directory_ack_gate.py').write_bytes(Path(__file__).read_bytes())
    print('Prepared separate optional one-ACK copy. No listener started; original source unchanged.')
def find_download_source():
    root=Path.home()/'storage'/'downloads'
    matches=[]
    for f in root.rglob('routed_probe_r037.py'):
        if f.stat().st_size>262144:continue
        if hashlib.sha256(f.read_bytes()).hexdigest()==R077_SHA:
            if (f.parent/'r076_private_route_equality.py').is_file():matches.append(f.parent)
    if len(matches)!=1:
        raise ValueError('Expected one prepared R077 folder in Android Download; found '+str(len(matches))+'. Use --source with its folder path.')
    return matches[0]

def find_original_library():
    explicit=os.environ.get('CF18_APOLLO_LIBRARY')
    candidates=([Path(explicit)] if explicit else [])
    candidates+=list((Path.home()/'storage'/'downloads').rglob('*apollo.so'))
    for f in candidates:
        if f.is_file() and f.stat().st_size==5243704:
            if hashlib.sha256(f.read_bytes()).hexdigest()=='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8':return f.resolve()
    raise ValueError('Exact original Apollo not found. Retain CF18_APOLLO_LIBRARY from your successful R077 run, or place that original library in Android Download.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source');p.add_argument('--output');p.add_argument('--print-library',action='store_true')
    a=p.parse_args()
    try:
        if a.print_library:print(find_original_library())
        else:
            if not a.output:p.error('--output required for preparation')
            prepare(a.source or find_download_source(),a.output)
    except (OSError,ValueError) as ex:raise SystemExit(str(ex))
