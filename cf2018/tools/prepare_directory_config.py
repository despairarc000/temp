"""Separate one-response startup configuration control; no listener starts here."""
import argparse,hashlib,os,shutil
from pathlib import Path
SOURCE_SHA='a2a2993bc644098765c4eb0a284e49bdf0616809857b8d23b12b06d13d34096c'
IDENTIFIER_SHA='e726b7df3927b4c49a0805219e34f004a6d5e2ac7ccf27936b7a178147573872'
OLD="""                        if second_service_probe:
                            status=('DIRECTORY_ROUTED_FRAME_OBSERVED' if sel == [[0x4013,5]] else 'DIRECTORY_OTHER_FRAME_OBSERVED')
                            later.append([kind,frame['frame_bytes'],0])
                            run.record('directory_post_stage_frame',cid,slot=slot,status=status,
                                       variant=kind,frame_bytes=frame['frame_bytes'],body_bytes=frame['body_bytes'],
                                       **classify_frame(raw_frame,_R077_ORIGINAL_ROUTE))
                            break
"""
NEW="""                        if second_service_probe:
                            profile=classify_frame(raw_frame,_R077_ORIGINAL_ROUTE)
                            if directory_replied:
                                status='FRAME_AFTER_DIRECTORY_REPLY'
                                later.append([kind,frame['frame_bytes'],0])
                                run.record('directory_after_reply_frame',cid,slot=slot,status=status,
                                           variant=kind,frame_bytes=frame['frame_bytes'],body_bytes=frame['body_bytes'],**profile)
                                break
                            run.record('directory_post_stage_frame',cid,slot=slot,status='DIRECTORY_REQUEST_CHECK',
                                       variant=kind,frame_bytes=frame['frame_bytes'],body_bytes=frame['body_bytes'],**profile)
                            if profile.get('directory_request')!='BY_ID_COMPLETE' or profile.get('directory_encoding')!='LEGACY64':
                                status='DIRECTORY_REPLY_REFUSED';break
                            candidate=make_directory_config(raw_frame)
                            with run.lock:
                                if getattr(run,'directory_reply_claimed',False):
                                    status='DIRECTORY_REPLY_BUDGET_USED';break
                                run.directory_reply_claimed=True
                            self.request.sendall(candidate)
                            directory_replied=True
                            run.record('directory_config_reply_written',cid,slot=slot,status='CONFIG_REPLY_WRITTEN',reply_bytes=len(candidate))
                            status='deadline'
                            continue
"""
def patch(text,observe_seconds=None):
 if observe_seconds is not None and (type(observe_seconds) is not int or not 60<=observe_seconds<=300):raise ValueError('observation window must be an integer from60 to300 seconds')
 if hashlib.sha256(text.encode()).hexdigest()!=SOURCE_SHA:raise ValueError('exact directory identifier source required')
 if text.count(OLD)!=1:raise ValueError('application-frame anchor changed')
 text=text.replace(OLD,NEW,1)
 text=text.replace('from directory_identify import classify_frame\n','from directory_identify import classify_frame\nfrom directory_config_reply import make_candidate as make_directory_config\n',1)
 text=text.replace('        second_service_probe=False\n','        second_service_probe=False\n        directory_replied=False\n',1)
 text=text.replace('CF2018_DIRECTORY_IDENTIFY','CF2018_DIRECTORY_CONFIG').replace('cf2018_directory_identify_runs','cf2018_directory_config_runs')
 text=text.replace('CF2018 directory auth/Bingo control; explicit opt-in; not login','CF2018 default startup-directory configuration control; one reply; not login')
 anchor="    out+=['','DISCLAIMERS:"
 if text.count(anchor)!=1:raise ValueError('report anchor changed')
 extra="""    for e in ev:
        if e['action'] in ('directory_config_reply_written','directory_after_reply_frame'):
            out.append('DIRECTORY_CONFIG slot='+str(e['slot'])+' event='+e['action']+' status='+str(e.get('status','UNKNOWN'))+' type='+str(e.get('variant','none'))+' bytes='+str(e.get('reply_bytes',e.get('frame_bytes',0)))+' request='+str(e.get('directory_request','NOT_APPLICABLE')))
"""
 text=text.replace(anchor,extra+anchor,1)
 if observe_seconds is not None:text=observation_patch(text,observe_seconds)
 compile(text,'directory configuration control','exec');return text

def observation_patch(text,seconds):
 # Called only after the exact-source gate and normal reply preparation.
 def replace_once(old,new):
  nonlocal text
  if text.count(old)!=1:raise ValueError('observation anchor changed')
  text=text.replace(old,new,1)
 replace_once('MAX_SLOTS=4\n',f'RESOURCE_OBSERVATION_SECONDS={seconds}\n'+OBSERVATION_HELPER+'\nMAX_SLOTS=4\n')
 replace_once('while time.monotonic()-started<12.0:',f'while time.monotonic()-started<{seconds}.0:')
 replace_once("        while not run.done.wait(.2):\n            if proc and proc.poll() is not None:raise RuntimeError('SOCKS5 proxy exited')",'        resource_observation_wait(run,proc)')
 replace_once("    out+=['','DISCLAIMERS:","    out.append('RESOURCE_OBSERVATION configured_seconds='+str(RESOURCE_OBSERVATION_SECONDS)+' elapsed_seconds='+str(getattr(run,'observation_elapsed','UNKNOWN'))+' stop='+str(getattr(run,'observation_stop','NOT_STARTED')))\n    out+=['','DISCLAIMERS:")
 replace_once("        print('PCAPdroid SOCKS5",f"        print('Resource observation: proxy stays available for{seconds} seconds; same replies and four-session cap. Ctrl+C stops early.')\n        print('PCAPdroid SOCKS5")
 return text

OBSERVATION_HELPER="""def resource_observation_wait(run,proc):
    # Session-budget completion must not terminate the proxy during resource check.
    run.observation_started=time.monotonic()
    run.observation_stop='interrupted_or_error'
    try:
        while time.monotonic()-run.observation_started<RESOURCE_OBSERVATION_SECONDS:
            if proc and proc.poll() is not None:
                run.observation_stop='proxy_exit'
                raise RuntimeError('SOCKS5 proxy exited')
            time.sleep(.2)
        run.observation_stop='window_elapsed'
    except KeyboardInterrupt:
        run.observation_stop='manual_stop'
        raise
    finally:
        run.observation_elapsed=round(time.monotonic()-run.observation_started,2)
"""

def prepare(source,output,observe_seconds=None):
 source=Path(source).resolve();output=Path(output).resolve()
 if output.exists() or source==output or source in output.parents:raise ValueError('new separate output directory required')
 if any(p.is_symlink() for p in source.rglob('*')):raise ValueError('source symlinks refused')
 text=patch((source/'routed_probe_r037.py').read_text(),observe_seconds)
 for name,sha in [('directory_identify.py',IDENTIFIER_SHA),('directory_ack_gate.py','f50b39c587c25465c23984285dc8934c3d4fb428390e87411dc3f86416dd2b27'),('second_service_syn_gate.py','9f7ee1969541ca27a1da48a4f91d4edab89d726383c71513efbe6e357072a43e')]:
  if hashlib.sha256((source/name).read_bytes()).hexdigest()!=sha:raise ValueError('original parser/gate helper changed')
 shutil.copytree(source,output);(output/'routed_probe_r037.py').write_text(text);(output/'directory_config_reply.py').write_text(REPLY_SOURCE)
 print('Prepared separate one-response copy. No listener started; original sources and game unchanged.')

def find_library():
 explicit=os.environ.get('CF18_APOLLO_LIBRARY')
 candidates=([Path(explicit)] if explicit else [])+list((Path.home()/'storage'/'downloads').rglob('*apollo.so'))
 for path in candidates:
  if path.is_file() and path.stat().st_size==5243704 and hashlib.sha256(path.read_bytes()).hexdigest()=='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8':return path.resolve()
 raise ValueError('Exact original Apollo not found in Android Download or CF18_APOLLO_LIBRARY.')
REPLY_SOURCE='"""Bounded synthetic startup-directory result. No sockets or credential handling.\n\nUses the build\'s source-selected configuration node and empty application data,\nwhich exercises the original VersionCustomRoot default-constructor path.\n"""\nMETHOD=b\'DirService:get_server_dirtree_by_id\'\nROUTE=b\'DirService\'\nNODE_ID=0x01010100\n\ndef vi(n):\n if type(n) is not int or not 0<=n<2**64:raise ValueError(\'bounded unsigned value\')\n b=bytearray()\n while n>=128:b.append((n&127)|128);n>>=7\n return bytes(b)+bytes([n])\ndef field(n,k,v):\n tag=vi(n<<4|k)\n if k==0:return tag+vi(v)\n if k==1 and type(v) is int and 0<=v<=255:return tag+bytes([v])\n if k==5 and type(v) is bytes and len(v)<=2048:return tag+len(v).to_bytes(4,\'big\')+v\n raise ValueError(\'TLV field shape\')\ndef node():\n custom=field(1,0,0)+field(2,0,0)+field(3,5,b\'\')\n category=field(1,0,0)+field(2,0,NODE_ID<<1)+field(3,0,0)+field(4,5,b\'\')+field(5,0,0)+field(6,5,custom)\n content=field(1,0,0)+field(2,5,field(0,5,category))\n return b\'\\xaa\'+(5+len(content)).to_bytes(4,\'big\')+content\n\ndef thrift_field(kind,number,value):return bytes([kind])+number.to_bytes(2,\'big\')+value\n\ndef component():\n tree=thrift_field(8,1,(1).to_bytes(4,\'big\'))+thrift_field(11,2,len(node()).to_bytes(4,\'big\')+node())+thrift_field(15,3,b\'\\x0c\'+bytes(4))+b\'\\0\'\n result=thrift_field(8,1,bytes(4))+thrift_field(11,2,bytes(4))+thrift_field(15,3,b\'\\x0c\'+(1).to_bytes(4,\'big\')+tree)+b\'\\0\'\n return thrift_field(12,0,result)+b\'\\0\'\n\ndef rpc(sequence):\n if type(sequence) is not int or not 0<=sequence<2**64:raise ValueError(\'RPC u64 required\')\n return len(METHOD).to_bytes(4,\'big\')+METHOD+b\'\\x02\'+sequence.to_bytes(8,\'big\')+component()\n\ndef request_correlation(frame):\n from directory_identify import classify_frame\n from routed_fingerprint_v21 import route_value_and_body\n from tgcp_wire import fields,require_field\n d=classify_frame(frame,ROUTE)\n if d.get(\'directory_request\')!=\'BY_ID_COMPLETE\' or d.get(\'directory_encoding\')!=\'LEGACY64\':raise ValueError(\'complete original BY_ID legacy request required\')\n end=2+int.from_bytes(frame[3:7],\'big\');base=fields(require_field(fields(frame[7:end]),1,5).value)\n packet_sequence=require_field(base,7,0).value\n _,body=route_value_and_body(frame)\n pos=4+4+len(METHOD)+1\n return packet_sequence,int.from_bytes(body[pos:pos+8],\'big\')\n\ndef make_candidate(frame):\n packet_seq,rpc_seq=request_correlation(frame)\n response=rpc(rpc_seq)\n # Same AA and DataHead family already exercised by the discovery response.\n # Server body starts at RPC header, not the client\'s 4B packet-sequence prefix.\n values=[0x4366,0,1,0x4013,0,0,packet_seq,0,len(response)]\n base=b\'\'.join(field(i,1 if i==6 else 0,v) for i,v in enumerate(values,1))\n route=field(4,5,field(1,5,ROUTE))\n data=field(1,1,0)+field(2,1,0)+field(3,1,1)+field(4,5,route)\n header=field(1,5,base)+field(2,5,field(0x4013,5,data))\n wire=b\'\\xaa\'+(5+len(header)).to_bytes(4,\'big\')+header+response\n if len(wire)>1024:raise ValueError(\'response size bound\')\n return wire\n'

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',default=str(Path.home()/'cf2018_directory_identify'));p.add_argument('--output');p.add_argument('--print-library',action='store_true');p.add_argument('--observe-seconds',type=int,help='optional60..300s proxy observation window; same one-reply gates');a=p.parse_args()
 try:
  if a.print_library:print(find_library())
  else:
   if not a.output:p.error('--output required for preparation')
   prepare(a.source,a.output,a.observe_seconds)
 except (OSError,ValueError) as ex:raise SystemExit(str(ex))
