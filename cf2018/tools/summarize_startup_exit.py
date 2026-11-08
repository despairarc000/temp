#!/usr/bin/env python3
"""Read existing Android exit/crash records; never launch, install or clear logs."""
import argparse,datetime,json,re,subprocess,uuid
from collections import Counter
from pathlib import Path

PACKAGE='com.tencent.tmgp.cfmnac'
MAX_BYTES=8*1024*1024
REASONS={0:'UNKNOWN',1:'EXIT_SELF',2:'SIGNALED',3:'LOW_MEMORY',4:'JAVA_CRASH',
         5:'NATIVE_CRASH',6:'ANR',7:'INITIALIZATION_FAILURE',8:'PERMISSION_CHANGE',
         9:'EXCESSIVE_RESOURCE_USAGE',10:'USER_REQUESTED',11:'USER_STOPPED',
         12:'DEPENDENCY_DIED',13:'OTHER',14:'FREEZER',15:'PACKAGE_STATE_CHANGE',16:'PACKAGE_UPDATED'}
MARKERS={
 'NETWORK_SECURITY_CONFIG':re.compile(r'NetworkSecurityConfig|XmlConfigSource|network security config',re.I),
 'RESOURCE_NOT_FOUND':re.compile(r'android\.content\.res\.Resources\$NotFoundException'),
 'XML_PARSE_ERROR':re.compile(r'XmlPullParserException'),
 'CERTIFICATE_ERROR':re.compile(r'CertificateException|CertificateParsingException'),
 'LINK_ERROR':re.compile(r'UnsatisfiedLinkError'),
 'SECURITY_EXCEPTION':re.compile(r'java\.lang\.SecurityException'),
 'NULL_POINTER':re.compile(r'java\.lang\.NullPointerException')}
BRIEF=re.compile(r'^[VDIWEF]/AndroidRuntime\s*\(\s*(\d+)\s*\):\s?(.*)$')
APK_ROLES={
 '33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9':'ORIGINAL',
 'e851f9f236afe2042f21acf2cd5bd74720d087800c35e4da94996f3fa89c2797':'SIGNATURE_CONTROL_A',
 '32f31159691b413e53de4fdcf3c3f5fe5ccd35f282ecb56d5e0cc88a38a957df':'SCOPED_TRUST_B'}

def timestamp(text):
    match=re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{1,6})?',text)
    if not match:return None
    value=match[0]
    try:return datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S.%f' if '.' in value else '%Y-%m-%d %H:%M:%S')
    except ValueError:return None

def exit_records(raw,updated_since=None):
    if len(raw)>MAX_BYTES:raise ValueError('bounded input required')
    records=[]
    for block in re.split(r'ApplicationExitInfo\s*#\d+\s*:',raw.decode('utf8',errors='replace'))[1:]:
        if not re.search(r'\bprocess='+re.escape(PACKAGE)+r'(?=\s|$)',block):continue
        reason=re.search(r'(?<!\w)reason=(\d{1,3})(?!\d)',block)
        if not reason:continue
        code=int(reason[1]);record={'reason':REASONS.get(code,'UNRECOGNIZED_REASON')}
        status=re.search(r'(?<!\w)status=(-?\d{1,4})(?!\d)',block)
        if status:
            value=int(status[1])
            if code==1:
                record['status']='ZERO' if value==0 else 'NONZERO'
                record['exit_status_code']=value if 0<=value<=255 else 'OUT_OF_RANGE'
            elif code==2:record['signal']={6:'SIGABRT',9:'SIGKILL',11:'SIGSEGV'}.get(value,'OTHER_SIGNAL')
        stamp=re.search(r'(?<!\w)timestamp=([^\r\n]+)',block)
        exited=timestamp(stamp[1]) if stamp else None
        record['relative_to_current_package_update']='UNKNOWN'
        if exited is not None and updated_since is not None:
            record['relative_to_current_package_update']='AT_OR_AFTER_UPDATE' if exited>=updated_since else 'BEFORE_UPDATE'
        records.append(record)
        if len(records)==3:break
    return records

def crash_mentions(raw):
    if len(raw)>MAX_BYTES:raise ValueError('bounded input required')
    events=[];active={}
    for line in raw.decode('utf8',errors='replace').splitlines():
        match=BRIEF.fullmatch(line)
        if not match:continue
        pid,message=match.groups()
        if message.startswith('FATAL EXCEPTION:'):
            event={'target':False,'markers':set()};active[pid]=event;events.append(event)
        event=active.get(pid)
        if event is None:continue
        process=re.fullmatch(r'Process: ([A-Za-z0-9_.:]+), PID: (\d+)',message)
        if process:event['target']=process[1]==PACKAGE and process[2]==pid
        for key,pattern in MARKERS.items():
            if pattern.search(message):event['markers'].add(key)
    matched=[e for e in events if e['target']]
    counts=Counter(k for e in matched for k in e['markers'])
    return {'target_java_fatal_records':len(matched),'fixed_mentions':dict(sorted(counts.items()))}

def adb_read(args):
    try:
        result=subprocess.run(['adb']+args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                              timeout=20,check=False)
        if result.returncode:return b'','UNAVAILABLE'
        if len(result.stdout)>MAX_BYTES:return b'','TOO_LARGE'
        return result.stdout,'READ'
    except (OSError,subprocess.TimeoutExpired):return b'','UNAVAILABLE'

def read_existing():
    results={};states={}
    commands={'exit_info':['shell','dumpsys','activity','exit-info',PACKAGE],
              'crash_buffer':['logcat','-b','crash','-d','-t','256','-v','brief']}
    for key,args in commands.items():results[key],states[key]=adb_read(args)
    return results,states

def read_identity():
    metadata,state=adb_read(['shell','dumpsys','package',PACKAGE])
    dates=re.findall(r'(?m)^\s*lastUpdateTime=([^\r\n]+)',metadata.decode('utf8',errors='replace'))
    updated=timestamp(dates[0]) if len(dates)==1 else None
    identity={'package_metadata':state,'update_time_parsed':updated is not None,'installed_apk':'UNKNOWN'}
    paths,path_state=adb_read(['shell','pm','path',PACKAGE]);identity['apk_path_read']=path_state
    paths=paths.decode('utf8',errors='replace').strip().splitlines()
    if len(paths)!=1:return identity,updated
    match=re.fullmatch(r'package:(/data/app/[A-Za-z0-9_./~+=-]+/base\.apk)',paths[0])
    if not match:return identity,updated
    raw,hash_state=adb_read(['shell','sha256sum',match[1]]);identity['apk_hash_read']=hash_state
    value=raw.split(maxsplit=1)[0].decode('ascii',errors='replace') if raw.strip() else ''
    if re.fullmatch('[a-fA-F0-9]{64}',value):identity['installed_apk']=APK_ROLES.get(value.lower(),'OTHER_APK')
    return identity,updated

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=Path.home()/'storage/downloads')
    args=parser.parse_args()
    raw,states=read_existing()
    identity,updated=read_identity()
    report={'format':'CF2018_STARTUP_EXIT_SUMMARY','acquisition':states,
            'installed_identity':identity,
            'main_process_exit_records_in_dump_order':exit_records(raw['exit_info'],updated),
            'crash_buffer':crash_mentions(raw['crash_buffer']),
            'attempt_attribution':'HISTORICAL_BUFFER_UPDATE_TIME_COMPARISON_NOT_ATTEMPT_BOUND',
            'integrity_cause':'NOT_ESTABLISHED',
            'limits':'Exit-self is not integrity proof; missing crash records are not a normal-exit result.'}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:8]
    path=args.output_dir/('CF2018_STARTUP_EXIT_'+stamp+'.txt')
    try:
        with path.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    except OSError:parser.exit(1,'No report written: output folder unavailable.\n')
    print('Saved '+str(path))
    if 'READ' not in states.values():print('ADB reads unavailable: reconnect Wireless debugging before repeating this reader.')
    print('Fixed labels only. No game launch, installation, log clearing or raw-log export.')

if __name__=='__main__':main()
