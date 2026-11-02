"""Prepare a separate bounded directory auth/Bingo observation; never starts it."""
import argparse,hashlib,shutil
from pathlib import Path
SOURCE_SHA='829398e786fa78aa9d2f83f6f3cca5a0c861962b415712533f7078744f26a9db'
HELPER_SHA='f50b39c587c25465c23984285dc8934c3d4fb428390e87411dc3f86416dd2b27'
OLD="""                        if second_service_probe:
                            status=('AUTH_REQUEST_OBSERVED' if sel == [[0x2001,1]] else 'OTHER_FRAME_OBSERVED')
                            run.record('second_service_followup',cid,slot=slot,status=status)
                            break
"""
NEW="""                        if second_service_probe:
                            status=('AUTH_REQUEST_OBSERVED' if sel == [[0x2001,1]] else 'OTHER_FRAME_OBSERVED')
                            run.record('second_service_followup',cid,slot=slot,status=status)
                            if sel != [[0x2001,1]]:break
                            if len(auth)!=54 or stage is None or len(stage)!=91:
                                raise ValueError('established synthetic stage sizes changed')
                            self.request.sendall(auth)
                            sent_auth=len(auth);auth_sent_time=time.monotonic()
                            run.record('directory_auth_written',cid,slot=slot,reply_bytes=sent_auth)
                            time.sleep(.15)
                            self.request.sendall(stage)
                            sent_stage=len(stage);stage_sent_time=time.monotonic()
                            run.record('directory_bingo_written',cid,slot=slot,reply_bytes=sent_stage)
                            status='deadline'
                            continue
"""
ANCHOR='                    else:\n                        elapsed=round('
INSERT="""                    else:
                        if second_service_probe:
                            status=('DIRECTORY_ROUTED_FRAME_OBSERVED' if sel == [[0x4013,5]] else 'DIRECTORY_OTHER_FRAME_OBSERVED')
                            later.append([kind,frame['frame_bytes'],0])
                            run.record('directory_post_stage_frame',cid,slot=slot,status=status,
                                       variant=kind,frame_bytes=frame['frame_bytes'],body_bytes=frame['body_bytes'])
                            break
                        elapsed=round("""
def patch(text):
    if hashlib.sha256(text.encode()).hexdigest()!=SOURCE_SHA:raise ValueError('exact directory one-ACK source required')
    if text.count(OLD)!=1 or text.count(ANCHOR)!=1:raise ValueError('source anchors changed')
    text=text.replace(OLD,NEW,1).replace(ANCHOR,INSERT,1)
    text=text.replace('CF2018_DIRECTORY_ACK','CF2018_DIRECTORY_STAGE').replace('cf2018_directory_ack_runs','cf2018_directory_stage_runs')
    text=text.replace('directory one-ACK control; explicit opt-in; not login','directory auth/Bingo control; explicit opt-in; not login')
    marker='    for e in events:\n'
    # Add only a fixed, value-free event summary to the existing safe report.
    anchor="    out+=['','DISCLAIMERS:"
    if text.count(anchor)!=1:raise ValueError('report anchor changed')
    report="""    for e in ev:
        if e['action'] in ('directory_auth_written','directory_bingo_written','directory_post_stage_frame'):
            out.append('DIRECTORY_STAGE slot='+str(e['slot'])+' event='+e['action']+' status='+str(e.get('status','WRITTEN'))+' frame_bytes='+str(e.get('frame_bytes',e.get('reply_bytes',0)))+' body_bytes='+str(e.get('body_bytes',0)))
"""
    text=text.replace(anchor,report+anchor,1)
    compile(text,'directory stage probe','exec')
    return text

def prepare(source,output):
    source=Path(source).resolve();output=Path(output).resolve()
    if output.exists() or source==output or source in output.parents:raise ValueError('new separate output folder required')
    if any(p.is_symlink() for p in source.rglob('*')):raise ValueError('source symlinks refused')
    text=patch((source/'routed_probe_r037.py').read_text())
    if hashlib.sha256((source/'directory_ack_gate.py').read_bytes()).hexdigest()!=HELPER_SHA:raise ValueError('original directory ACK helper changed')
    shutil.copytree(source,output);(output/'routed_probe_r037.py').write_text(text)
    print('Prepared separate directory-stage copy. No listener started.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',default=str(Path.home()/'cf2018_directory_ack'));p.add_argument('--output',required=True)
    a=p.parse_args()
    try:prepare(a.source,a.output)
    except (OSError,ValueError) as ex:raise SystemExit(str(ex))
