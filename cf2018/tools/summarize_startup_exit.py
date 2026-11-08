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

def exit_records(raw):
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
            if code==1:record['status']='ZERO' if value==0 else 'NONZERO'
            elif code==2:record['signal']={6:'SIGABRT',9:'SIGKILL',11:'SIGSEGV'}.get(value,'OTHER_SIGNAL')
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

def read_existing():
    results={};states={}
    commands={'exit_info':['shell','dumpsys','activity','exit-info',PACKAGE],
              'crash_buffer':['logcat','-b','crash','-d','-t','256','-v','brief']}
    for key,args in commands.items():
        try:
            result=subprocess.run(['adb']+args,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                  timeout=20,check=False)
            if result.returncode:states[key]='UNAVAILABLE';results[key]=b''
            elif len(result.stdout)>MAX_BYTES:states[key]='TOO_LARGE';results[key]=b''
            else:states[key]='READ';results[key]=result.stdout
        except (OSError,subprocess.TimeoutExpired):states[key]='UNAVAILABLE';results[key]=b''
    return results,states

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=Path.home()/'storage/downloads')
    args=parser.parse_args()
    raw,states=read_existing()
    report={'format':'CF2018_STARTUP_EXIT_SUMMARY','acquisition':states,
            'main_process_exit_records_in_dump_order':exit_records(raw['exit_info']),
            'crash_buffer':crash_mentions(raw['crash_buffer']),
            'attempt_attribution':'HISTORICAL_BUFFER_NOT_BOUND_TO_THIS_INSTALL_OR_ATTEMPT',
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
