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
def patch(text,observe_seconds=None,identify_address_queries=False):
 if identify_address_queries and observe_seconds is None:raise ValueError('address identification requires a bounded observation window')
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
 # A run start timestamp plus its random suffix identifies every deliverable.
 old="Path.home()/'storage/downloads/CF2018_DIRECTORY_CONFIG_Result.txt'"
 new="Path.home()/'storage/downloads'/('CF2018_DIRECTORY_CONFIG_Result_'+run.base.name+'.txt')"
 if text.count(old)!=1:raise ValueError('result filename anchor changed')
 text=text.replace(old,new,1)
 old="    target.write_text('\\n'.join(out)+'\\n',encoding='utf8')"
 new="    with target.open('x',encoding='utf8') as stream:stream.write('\\n'.join(out)+'\\n')"
 if text.count(old)!=1:raise ValueError('result writer anchor changed')
 text=text.replace(old,new,1)
 anchor="    target.parent.mkdir(parents=True,exist_ok=True)"
 extra="    out.insert(1,'REPORT_ID '+run.base.name)\n    for slot in sorted(set(accepted)-{e['slot'] for e in rows}):\n        out.append('SESSION_OPEN_AT_REPORT slot='+str(slot))\n"
 if text.count(anchor)!=1:raise ValueError('report identity anchor changed')
 text=text.replace(anchor,extra+anchor,1)
 if observe_seconds is not None:text=observation_patch(text,observe_seconds)
 if identify_address_queries:text=address_identification_patch(text)
 compile(text,'directory configuration control','exec');return text

def observation_patch(text,seconds):
 # Called only after the exact-source gate and normal reply preparation.
 def replace_once(old,new):
  nonlocal text
  if text.count(old)!=1:raise ValueError('observation anchor changed')
  text=text.replace(old,new,1)
 replace_once('MAX_SLOTS=4\n',f'RESOURCE_OBSERVATION_SECONDS={seconds}\n'+OBSERVATION_HELPER+'\nMAX_SLOTS=4\n')
 replace_once('        self.run_id=uuid.uuid4().hex',"        self.observation_abort=threading.Event()\n        self.run_id=uuid.uuid4().hex")
 replace_once('        if slot>run.max_sessions:\n',"        if slot>run.max_sessions:\n            run.observation_abort.set()\n")
 replace_once('while time.monotonic()-started<12.0:',f'while time.monotonic()-started<{seconds}.0:')
 replace_once("        while not run.done.wait(.2):\n            if proc and proc.poll() is not None:raise RuntimeError('SOCKS5 proxy exited')",'        resource_observation_wait(run,proc)')
 replace_once("    out+=['','DISCLAIMERS:","    out.append('RESOURCE_OBSERVATION configured_seconds='+str(RESOURCE_OBSERVATION_SECONDS)+' elapsed_seconds='+str(getattr(run,'observation_elapsed','UNKNOWN'))+' stop='+str(getattr(run,'observation_stop','NOT_STARTED')))\n    out+=['','DISCLAIMERS:")
 replace_once("        print('PCAPdroid SOCKS5",f"        print('Resource observation: up to {seconds} seconds; first excess session stops the run. Same four-session cap. Ctrl+C stops early.')\n        print('PCAPdroid SOCKS5")
 return text

OBSERVATION_HELPER="""def resource_observation_wait(run,proc):
    # Preserve the bound without repeatedly closing retries for the full window.
    run.observation_started=time.monotonic()
    run.observation_stop='interrupted_or_error'
    try:
        while time.monotonic()-run.observation_started<RESOURCE_OBSERVATION_SECONDS:
            if run.observation_abort.is_set():
                run.observation_stop='session_budget_exhausted'
                return
            if getattr(run,'version_address_identified',False):
                run.observation_stop='version_address_identified'
                return
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

def address_identification_patch(text):
 def once(old,new):
  nonlocal text
  if text.count(old)!=1:raise ValueError('address identification anchor changed')
  text=text.replace(old,new,1)
 once('from directory_config_reply import make_candidate as make_directory_config\n','from directory_config_reply import make_candidate as make_directory_config\nfrom address_query_target import classify_frame as classify_address_target\n')
 anchor='                    else:\n                        if second_service_probe:'
 extra="""                    else:
                        if kind==0x4013:
                            target=classify_address_target(raw_frame)
                            run.record('address_query_target',cid,slot=slot,**target)
                            if target['address_target']=='VERSION_ADDRESS_QUERY':
                                run.version_address_identified=True
                                status='version_address_identified_no_reply'
                                break
                        if second_service_probe:"""
 once(anchor,extra)
 anchor="    out+=['','DISCLAIMERS:"
 extra="""    for e in ev:
        if e['action']=='address_query_target':
            out.append('ADDRESS_TARGET slot='+str(e['slot'])+' target='+e['address_target']+' reason='+e['address_target_reason'])
"""
 once(anchor,extra+anchor)
 return text

def prepare(source,output,observe_seconds=None,identify_address_queries=False):
 source=Path(source).resolve();output=Path(output).resolve()
 if output.exists() or source==output or source in output.parents:raise ValueError('new separate output directory required')
 if any(p.is_symlink() for p in source.rglob('*')):raise ValueError('source symlinks refused')
 text=patch((source/'routed_probe_r037.py').read_text(),observe_seconds,identify_address_queries)
 for name,sha in [('directory_identify.py',IDENTIFIER_SHA),('directory_ack_gate.py','f50b39c587c25465c23984285dc8934c3d4fb428390e87411dc3f86416dd2b27'),('second_service_syn_gate.py','9f7ee1969541ca27a1da48a4f91d4edab89d726383c71513efbe6e357072a43e')]:
  if hashlib.sha256((source/name).read_bytes()).hexdigest()!=sha:raise ValueError('original parser/gate helper changed')
 shutil.copytree(source,output);(output/'routed_probe_r037.py').write_text(text);(output/'directory_config_reply.py').write_text(REPLY_SOURCE)
 if identify_address_queries:(output/'address_query_target.py').write_text(ADDRESS_TARGET_SOURCE)
 print('Prepared separate one-response copy. No listener started; original sources and game unchanged.')

def find_library():
 explicit=os.environ.get('CF18_APOLLO_LIBRARY')
 candidates=([Path(explicit)] if explicit else [])+list((Path.home()/'storage'/'downloads').rglob('*apollo.so'))
 for path in candidates:
  if path.is_file() and path.stat().st_size==5243704 and hashlib.sha256(path.read_bytes()).hexdigest()=='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8':return path.resolve()
 raise ValueError('Exact original Apollo not found in Android Download or CF18_APOLLO_LIBRARY.')
REPLY_SOURCE='"""Bounded synthetic startup-directory result. No sockets or credential handling.\n\nUses the build\'s source-selected configuration node and empty application data,\nwhich exercises the original VersionCustomRoot default-constructor path.\n"""\nMETHOD=b\'DirService:get_server_dirtree_by_id\'\nROUTE=b\'DirService\'\nNODE_ID=0x01010100\n\ndef vi(n):\n if type(n) is not int or not 0<=n<2**64:raise ValueError(\'bounded unsigned value\')\n b=bytearray()\n while n>=128:b.append((n&127)|128);n>>=7\n return bytes(b)+bytes([n])\ndef field(n,k,v):\n tag=vi(n<<4|k)\n if k==0:return tag+vi(v)\n if k==1 and type(v) is int and 0<=v<=255:return tag+bytes([v])\n if k==5 and type(v) is bytes and len(v)<=2048:return tag+len(v).to_bytes(4,\'big\')+v\n raise ValueError(\'TLV field shape\')\ndef node():\n custom=field(1,0,0)+field(2,0,0)+field(3,5,b\'\')\n category=field(1,0,0)+field(2,0,NODE_ID<<1)+field(3,0,0)+field(4,5,b\'\')+field(5,0,0)+field(6,5,custom)\n content=field(1,0,0)+field(2,5,field(0,5,category))\n return b\'\\xaa\'+(5+len(content)).to_bytes(4,\'big\')+content\n\ndef thrift_field(kind,number,value):return bytes([kind])+number.to_bytes(2,\'big\')+value\n\ndef component():\n tree=thrift_field(8,1,(1).to_bytes(4,\'big\'))+thrift_field(11,2,len(node()).to_bytes(4,\'big\')+node())+thrift_field(15,3,b\'\\x0c\'+bytes(4))+b\'\\0\'\n result=thrift_field(8,1,bytes(4))+thrift_field(11,2,bytes(4))+thrift_field(15,3,b\'\\x0c\'+(1).to_bytes(4,\'big\')+tree)+b\'\\0\'\n return thrift_field(12,0,result)+b\'\\0\'\n\ndef rpc(sequence):\n if type(sequence) is not int or not 0<=sequence<2**64:raise ValueError(\'RPC u64 required\')\n return len(METHOD).to_bytes(4,\'big\')+METHOD+b\'\\x02\'+sequence.to_bytes(8,\'big\')+component()\n\ndef request_correlation(frame):\n from directory_identify import classify_frame\n from routed_fingerprint_v21 import route_value_and_body\n from tgcp_wire import fields,require_field\n d=classify_frame(frame,ROUTE)\n if d.get(\'directory_request\')!=\'BY_ID_COMPLETE\' or d.get(\'directory_encoding\')!=\'LEGACY64\':raise ValueError(\'complete original BY_ID legacy request required\')\n end=2+int.from_bytes(frame[3:7],\'big\');base=fields(require_field(fields(frame[7:end]),1,5).value)\n packet_sequence=require_field(base,7,0).value\n _,body=route_value_and_body(frame)\n pos=4+4+len(METHOD)+1\n return packet_sequence,int.from_bytes(body[pos:pos+8],\'big\')\n\ndef make_candidate(frame):\n packet_seq,rpc_seq=request_correlation(frame)\n response=rpc(rpc_seq)\n # Same AA and DataHead family already exercised by the discovery response.\n # Server body starts at RPC header, not the client\'s 4B packet-sequence prefix.\n values=[0x4366,0,1,0x4013,0,0,packet_seq,0,len(response)]\n base=b\'\'.join(field(i,1 if i==6 else 0,v) for i,v in enumerate(values,1))\n route=field(4,5,field(1,5,ROUTE))\n data=field(1,1,0)+field(2,1,0)+field(3,1,1)+field(4,5,route)\n header=field(1,5,base)+field(2,5,field(0x4013,5,data))\n wire=b\'\\xaa\'+(5+len(header)).to_bytes(4,\'big\')+header+response\n if len(wire)>1024:raise ValueError(\'response size bound\')\n return wire\n'

ADDRESS_TARGET_SOURCE='"""Read-only fixed-label address-query target discriminator. No reply generation.\n\nChecks the original legacy64 request grammar, complete consumption, packet\nsequence and route/clear transport guards. Labels refer to request content only,\nnot successful discovery, ownership, authentication or a version request itself.\n"""\nMETHOD=b\'QueryAddrSvr:QueryAddrInfo\'\n\ndef classify_body(body,sequence):\n    no={\'address_target\':\'NOT_IDENTIFIED\',\'address_target_reason\':\'SHAPE_MISMATCH\'}\n    if type(body) is not bytes or not 4<=len(body)<=1024 or type(sequence) is not int or not 0<=sequence<2**32:return no\n    if body[:4]!=sequence.to_bytes(4,\'big\'):\n        return {**no,\'address_target_reason\':\'PACKET_SEQUENCE_MISMATCH\'}\n    head=len(METHOD).to_bytes(4,\'big\')+METHOD+b\'\\1\'\n    if body[4:4+len(head)]!=head:return no\n    p=4+len(head)+8 # Independent RPC64 sequence, never returned.\n    if body[p:p+6]!=b\'\\x0c\\0\\1\\x0a\\0\\1\':return no\n    p+=6+8 # game_id is neither logged nor used as a substitute service label.\n    if body[p:p+3]!=b\'\\x0a\\0\\2\' or p+11>len(body):return no\n    unit=int.from_bytes(body[p+3:p+11],\'big\');p+=11\n    if body[p:p+3]!=b\'\\x0b\\0\\3\' or p+7>len(body):return no\n    n=int.from_bytes(body[p+3:p+7],\'big\');p+=7\n    if n>128 or p+n+2!=len(body) or body[-2:]!=b\'\\0\\0\':return no\n    service=body[p:p+n]\n    label={(b\'dir\',3):\'DIRECTORY_ADDRESS_QUERY\',(b\'download\',1):\'VERSION_ADDRESS_QUERY\'}.get((service,unit),\'OTHER_ADDRESS_QUERY\')\n    return {\'address_target\':label,\'address_target_reason\':\'COMPLETE_LEGACY64\'}\n\ndef classify_frame(frame):\n    no={\'address_target\':\'NOT_COMPARABLE\',\'address_target_reason\':\'FRAME_INVALID\'}\n    if type(frame) is not bytes or not 7<=len(frame)<=8192 or frame[:3]!=b\'\\x43\\x66\\xaa\':return no\n    try:\n        from tgcp_wire import fields,require_field\n        from routed_fingerprint_v21 import route_value_and_body\n        from gcloud_datahead_v38 import compression_from_routed_frame\n        end=2+int.from_bytes(frame[3:7],\'big\')\n        if not 7<=end<=len(frame):return no\n        outer=fields(frame[7:end]);base=fields(require_field(outer,1,5).value)\n        if require_field(base,9,0).value!=len(frame)-end:return no\n        if require_field(base,4,0).value!=0x4013:return no\n        if require_field(base,6,1).value!=0:return {**no,\'address_target_reason\':\'CIPHER_NOT_CLEAR\'}\n        if compression_from_routed_frame(frame).get(\'compression_flag\')!=\'no\':return {**no,\'address_target_reason\':\'COMPRESSION_NOT_CLEAR\'}\n        name,body=route_value_and_body(frame)\n        if name!=b\'QueryAddrSvr\':return {**no,\'address_target_reason\':\'ROUTE_MISMATCH\'}\n        return classify_body(body,require_field(base,7,0).value)\n    except (ValueError,TypeError,IndexError,OverflowError):return no\n'

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',default=str(Path.home()/'cf2018_directory_identify'));p.add_argument('--output');p.add_argument('--print-library',action='store_true');p.add_argument('--observe-seconds',type=int,help='optional60..300s maximum observation; stops at first excess session');p.add_argument('--identify-address-queries',action='store_true',help='label address targets; stop before replying to an identified version-address query');a=p.parse_args()
 try:
  if a.print_library:print(find_library())
  else:
   if not a.output:p.error('--output required for preparation')
   prepare(a.source,a.output,a.observe_seconds,a.identify_address_queries)
 except (OSError,ValueError) as ex:raise SystemExit(str(ex))
