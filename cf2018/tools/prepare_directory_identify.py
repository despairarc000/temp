"""Copy-only directory request identifier. Same bounded replies, no directory answer."""
import argparse,hashlib,shutil
from pathlib import Path
SOURCE_SHA='87a988a98ab56fb6d789a6faabc0ed8b26b685b06d4c3ea55542a94d27a46cb6'
METHODS={b'DirService:get_server_dirtree_all':('ALL_COMPLETE',((1,10),(2,11),(3,10))),b'DirService:get_server_dirtree_by_id':('BY_ID_COMPLETE',((1,10),(2,11),(3,8),(4,10))),b'DirService:get_server_by_ids':('BY_IDS_COMPLETE',((1,10),(2,11),(3,8),(4,8),(5,10)))}
def classify_body(body,sequence):
    no={'directory_request':'NOT_IDENTIFIED','directory_encoding':'UNKNOWN','directory_reason':'RPC_SHAPE_MISMATCH'}
    if type(body) is not bytes or not 4<=len(body)<=1024 or type(sequence) is not int or not 0<=sequence<2**32:return no
    if body[:4]!=sequence.to_bytes(4,'big'):
        no['directory_reason']='PACKET_SEQUENCE_MISMATCH';return no
    p=4;encoding='LEGACY64'
    if body[p:p+4]==b'\x80\x01\x00\x01':encoding='STRICT64';p+=4
    if p+4>len(body):return no
    n=int.from_bytes(body[p:p+4],'big');p+=4
    if n>64 or p+n>len(body):return no
    method=body[p:p+n];p+=n
    if method not in METHODS:
        no['directory_reason']='METHOD_NOT_ALLOWLISTED';return no
    if encoding=='LEGACY64':
        if p>=len(body) or body[p]!=1:return no
        p+=1
    if p+8>len(body):return no
    p+=8 # RPC sequence64; never exported, not TGCP sequence32.
    label,shape=METHODS[method]
    for field,kind in shape:
        if body[p:p+3]!=bytes([kind])+field.to_bytes(2,'big'):return no
        p+=3
        if kind==11:
            if p+4>len(body):return no
            size=int.from_bytes(body[p:p+4],'big');p+=4
            if size>256:return no
            p+=size
        else:p+=8 if kind==10 else 4
        if p>len(body):return no
    if body[p:]!=b'\0':return no
    return {'directory_request':label,'directory_encoding':encoding,'directory_reason':'COMPLETE'}

def classify_frame(frame,original_route):
    no={'directory_request':'NOT_COMPARABLE','directory_encoding':'UNKNOWN','directory_reason':'FRAME_INVALID'}
    if type(frame) is not bytes or len(frame)>8192 or frame[:3]!=b'\x43\x66\xaa':return no
    try:
        from tgcp_wire import fields,require_field
        from routed_fingerprint_v21 import route_value_and_body
        from gcloud_datahead_v38 import compression_from_routed_frame
        if type(frame) is not bytes or len(frame)>8192 or frame[:3]!=b'\x43\x66\xaa':return no
        end=2+int.from_bytes(frame[3:7],'big')
        if not 7<=end<=len(frame):return no
        outer=fields(frame[7:end]);base=fields(require_field(outer,1,5).value)
        if require_field(base,9,0).value!=len(frame)-end:return no
        if require_field(base,6,1).value!=0:
            no['directory_reason']='ENCRYPTED_FLAG_SET';return no
        if compression_from_routed_frame(frame).get('compression_flag')!='no':
            no['directory_reason']='COMPRESSION_NOT_CLEAR';return no
        name,body=route_value_and_body(frame)
        if name!=original_route or type(original_route) is not bytes or len(original_route)!=10:
            no['directory_reason']='ROUTE_MISMATCH';return no
        return classify_body(body,require_field(base,7,0).value)
    except (ValueError,TypeError,IndexError,OverflowError):return no

def patch(text):
    if hashlib.sha256(text.encode()).hexdigest()!=SOURCE_SHA:raise ValueError('exact previous directory-stage source required')
    anchor='from pathlib import Path\n'
    text=text.replace(anchor,anchor+'from directory_identify import classify_frame\n',1)
    anchor="variant=kind,frame_bytes=frame['frame_bytes'],body_bytes=frame['body_bytes'])"
    if text.count(anchor)!=1:raise ValueError('event anchor changed')
    text=text.replace(anchor,"variant=kind,frame_bytes=frame['frame_bytes'],body_bytes=frame['body_bytes'],\n                                       **classify_frame(raw_frame,_R077_ORIGINAL_ROUTE))",1)
    anchor="+' body_bytes='+str(e.get('body_bytes',0)))"
    if text.count(anchor)!=1:raise ValueError('report anchor changed')
    text=text.replace(anchor,"+' body_bytes='+str(e.get('body_bytes',0))+' request='+str(e.get('directory_request','NOT_APPLICABLE'))+' encoding='+str(e.get('directory_encoding','UNKNOWN'))+' reason='+str(e.get('directory_reason','NOT_APPLICABLE')))",1)
    text=text.replace('CF2018_DIRECTORY_STAGE','CF2018_DIRECTORY_IDENTIFY').replace('cf2018_directory_stage_runs','cf2018_directory_identify_runs')
    compile(text,'directory identifier','exec');return text

def prepare(source,output):
    source=Path(source).resolve();output=Path(output).resolve()
    if output.exists() or source==output or source in output.parents:raise ValueError('new separate output required')
    if any(p.is_symlink() for p in source.rglob('*')):raise ValueError('symlinks refused')
    text=patch((source/'routed_probe_r037.py').read_text())
    if hashlib.sha256((source/'directory_ack_gate.py').read_bytes()).hexdigest()!='f50b39c587c25465c23984285dc8934c3d4fb428390e87411dc3f86416dd2b27':raise ValueError('directory gate changed')
    shutil.copytree(source,output);(output/'routed_probe_r037.py').write_text(text);(output/'directory_identify.py').write_bytes(Path(__file__).read_bytes())
    print('Prepared separate identifier. No listener started; no directory response added.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',default=str(Path.home()/'cf2018_directory_stage'));p.add_argument('--output',required=True);a=p.parse_args()
    try:prepare(a.source,a.output)
    except (OSError,ValueError) as ex:raise SystemExit(str(ex))
