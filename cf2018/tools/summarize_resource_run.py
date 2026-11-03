#!/usr/bin/env python3
"""Summarize existing Termux run metadata. No game, listener or network calls.

Exports fixed labels/counts only. Hosts are compared in memory against hashes
of DNS names from the exact original settings resource; IPs remain unclassified.
"""
import argparse,hashlib,ipaddress,json,re,uuid
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

KNOWN_HOSTS={
  "11a600bd2baa1fb4c00be59f38d87fbfb2953ea1f8e1001420f18f2aa34b8a52": "DIRECTORY",
  "16a75c3699b4861dff228b6518ca57b75f3b653a78e9bc7d17879ec98b861df9": "DIRECTORY",
  "19ff92e7ef33651b0a9edca3f2879b9390adb9af960d2eb302431d074426f14b": "DIRECTORY",
  "20fef9cce240f636ee557ab03d74dc0d36f35d0ff6b2ba1a58aeb9003d0b1a85": "ASSET",
  "2c8c17e611245d338a656ebaddb84ea74f32a874f466e6aff906a34a1de3aef5": "ASSET",
  "30c90a03966f98c2b28818a24b9ba1a7e286804a25b68440f07bbb7074aeb0c4": "DIRECTORY",
  "3667e59f641a74e83fe486fd37d496610f86253620302dcb6ef7a837490861cb": "ASSET",
  "3994613055b95aacdc1330ba07c5cecb71a2bb3926b94e4c243bed7ef03aabe1": "DIRECTORY",
  "3dcb39cd1eafc3945ca31159fa9ba819f6c53ee72efbeb6f6b063c4ad4fecd8d": "VERSION",
  "43e29a1917ce4d6618b3aff8fd1019b82089de34651c11dbbfb7828db33e8b6f": "DIRECTORY",
  "494b2a0524b9fd16bab8c556d619cb041a3fafc3957905dfb5bad58654607b7a": "ASSET",
  "496badd98317107961c3db1fad0b07c7704185b4fc715d577cd171138d2bf2e4": "DIRECTORY",
  "4a3a977930e2b0e139c6a2145f1f656aad4bd8af77bc21ae027d4a0c3a2fb73f": "DIRECTORY",
  "4d3d7afb2f3effd1b8f7b5143cd10a59a85c0e150a8537c30f6eb11e8b9cad39": "DIRECTORY",
  "60fa0a2fac9b7d1ba1d7dd866d303633c794584909c7669e27efdd426c49412b": "VERSION",
  "71b87098af7e14e520ab4803e09b7b22b2b10aed3763484c6bbc9eb0f2751683": "DIRECTORY",
  "78bcccc1e160b94ea8236df7df9582fba63178b71d64cfe7aba069166693f800": "DIRECTORY",
  "7b090d346fec54ff624d8b5efec414477091f225515feae4bc2b98b6b650d1e1": "VERSION",
  "855cdbe19fc60912e44e1b8cf8dca42539dd64b9bf99591f82c0ac165ef7dad9": "VERSION",
  "8dc778f2b098ad4db940f2cc414679a8a9d226fc96f42fa41fe6a5bc2c63975d": "VERSION",
  "934503c20c7dde40c01c99af997545ac6c9c5068e92cfa591388e2a4848d9ce8": "DIRECTORY",
  "9655f8568827dd42dd0b18d9d81ba92316cd06936e5966ee17d84774b50aff2c": "VERSION",
  "9a6105cd2da4947ff810c76ce331a4287b5b1c3d8508e4bd8281b3e5c975e1f2": "VERSION",
  "9aaee8182534a105590b6aa36faeea010f4733c8b86d0fa059379768a84b3302": "VERSION",
  "b79a713ab5b85f9b01cb52c0e3d40c653f1690b5076554b0b1490b6d173f0aed": "VERSION",
  "c4f6896eca558112b9d3280bfce8c2449a023c5409ae7ea7b9b745ca663c77af": "ASSET",
  "c7ec50aa49778a97f78008de0eb142c733507fec56d75594e69dcaf544972fe5": "DIRECTORY",
  "cd35176eb14ebf0dc7c9ad411a7a9cddc11fe42b5fb026ea31225e4d273094f6": "VERSION",
  "df7a4de1bc619b339d58f560215a62db2ae55c5fd513a9e8a141663a5aaca399": "VERSION",
  "e801725ca387ed070959a3f57acdf7f36422935a462b4cbbb74fac16e257faef": "VERSION",
  "eac6f69f4304f427c429411a059e3b760f0bc9502aafc8c57e3de642165600a3": "DIRECTORY",
  "ed97c261f69d6ab5796520ba745ca93008b493d4378a6f2e46ea698f1415eb02": "ASSET",
  "f4db7c97650d529a2c098d872d0ad80e8e2bf7bac48a180868b42bb5c078ee47": "VERSION",
  "f704b3934f20d8cf1cdbf76fff6b30a41c22310bf0824d99c95d229b43f23c48": "VERSION",
  "fe703d0063b62eac821420a9fb6a656bf039a77dbaee6399323b5d47bfe753c2": "ASSET"
}
MAX_BYTES=8*1024*1024
MAX_LINES=50000
MAX_LINE=8192
RUN_NAME=re.compile(r'run_[0-9]{8}T[0-9]{6}Z_[0-9a-f]{8}')

def host_label(value,known=None):
    if type(value) is not str or len(value)>253:return 'UNKNOWN'
    host=value.strip().lower().rstrip('.')
    try:ipaddress.ip_address(host);return 'UNCLASSIFIED_IP'
    except ValueError:pass
    label=(KNOWN_HOSTS if known is None else known).get(hashlib.sha256(host.encode()).hexdigest())
    return label if label in ('DIRECTORY','VERSION','ASSET') else 'UNCLASSIFIED_NAME'

def port_label(value):
    return str(value) if type(value) is int and value in (80,443,8080,8085) else 'OTHER'

def records(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('metadata file missing or symlink refused')
    before=path.stat()
    if before.st_size>MAX_BYTES:raise ValueError('metadata file exceeds read limit')
    events=[];invalid=0
    with path.open('rb') as stream:
        for number in range(MAX_LINES+1):
            raw=stream.readline(MAX_LINE+1)
            if not raw:break
            if number==MAX_LINES or len(raw)>MAX_LINE:raise ValueError('metadata line/read limit exceeded')
            try:
                event=json.loads(raw)
                if type(event) is not dict:raise ValueError()
                events.append(event)
            except (ValueError,UnicodeError):invalid+=1
    after=path.stat()
    stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    return events,invalid,stable

def summarize(run_dir,known=None):
    run_dir=Path(run_dir)
    if run_dir.is_symlink() or not run_dir.is_dir() or (run_dir/'relay').is_symlink():raise ValueError('run directory missing or symlink refused')
    server,bad_server,stable_server=records(run_dir/'events.jsonl')
    relay,bad_relay,stable_relay=records(run_dir/'relay'/'events.jsonl')
    accepted=set();finished=set();counts=Counter();reply_seen=False
    run_ids={e['run_id'] for e in server if type(e.get('run_id')) is str and re.fullmatch(r'[0-9a-f]{32}',e['run_id'])}
    for event in server:
        action=event.get('action');slot=event.get('slot')
        if type(slot) is not int or not 0<slot<=MAX_LINES:continue
        if action=='accepted':accepted.add(slot)
        elif action=='finished':
            finished.add(slot)
            if event.get('reason')=='over_cap':
                counts['over_cap']+=1
                counts['over_cap_after_settings']+=int(reply_seen)
        elif action=='directory_config_reply_written':counts['settings_replies']+=1;reply_seen=True
        elif action=='r033_reply_sent':counts['discovery_replies']+=1
        elif action=='later_client_frame' and event.get('variant')==0x4013 and event.get('qualified_address_request')=='COMPLETE_STRUCTURAL_CANDIDATE':counts['address_candidates']+=1
    rows={};connections={};duplicates=0
    for event in relay:
        kind=event.get('event');cid=event.get('connection')
        if type(cid) is not int or not 0<cid<=MAX_LINES:continue
        if kind in ('CONNECTED','CONNECT_FAILED'):
            role=host_label(event.get('host'),known);status=event.get('status')
            mode=status if status in ('EMULATOR','PASSTHROUGH') else 'UNKNOWN'
            key=(role,mode,port_label(event.get('port')))
            if cid in connections:duplicates+=1;continue
            connections[cid]=key;row=rows.setdefault(key,Counter());row[kind]+=1
        elif kind=='RELAY_BYTES' and cid in connections:
            direction=event.get('direction');value=event.get('bytes')
            if direction in ('client->server','server->client') and type(value) is int and 0<=value<=10**10:
                rows[connections[cid]][direction]+=value
    reference=run_dir.name if RUN_NAME.fullmatch(run_dir.name) else 'UNQUALIFIED_NAME'
    out=['CF2018 existing resource-run metadata summary','SOURCE_RUN '+reference,
         'READ_STABILITY '+('STABLE' if stable_server and stable_relay else 'CHANGED_DURING_READ'),
         'INVALID_JSON_LINES '+str(bad_server+bad_relay),
         'SERVER_RUN_ID_COUNT '+str(len(run_ids)),
         'SERVER accepted='+str(len(accepted))+' finished='+str(len(finished))+' open_at_snapshot='+str(len(accepted-finished))+' over_cap='+str(counts['over_cap'])+' over_cap_after_settings='+str(counts['over_cap_after_settings'])+' settings_replies='+str(counts['settings_replies'])+' discovery_replies='+str(counts['discovery_replies'])+' address_candidates='+str(counts['address_candidates']),
         'RELAY duplicate_connection_ids='+str(duplicates)]
    for (role,mode,port),row in sorted(rows.items()):
        out.append('RELAY class='+role+' mode='+mode+' port='+port+' connected='+str(row['CONNECTED'])+' connect_failed='+str(row['CONNECT_FAILED'])+' client_bytes='+str(row['client->server'])+' server_bytes='+str(row['server->client']))
    out+=['SERVICE_LABELS hostname matches only; IP/shared frontend does not identify a service or RPC method.',
          'TIMING server metadata has no timestamps; cross-file timing/connection joins are UNKNOWN.',
          'No hostnames, addresses, payloads, identifiers, credentials or raw error text exported. No game/server started.']
    return '\n'.join(out)+'\n'

def choose_run(root):
    root=Path(root)
    candidates=[p for p in root.glob('run_*') if RUN_NAME.fullmatch(p.name) and not p.is_symlink() and p.is_dir() and (p/'events.jsonl').is_file() and (p/'relay'/'events.jsonl').is_file()]
    if not candidates:raise ValueError('no saved configuration-run metadata found')
    return max(candidates,key=lambda p:p.name)

def write_summary(run_dir,output_dir,known=None):
    text=summarize(run_dir,known)
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    name='CF2018_RESOURCE_RUN_SUMMARY_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:8]+'.txt'
    target=output_dir/name
    with target.open('x',encoding='utf8') as stream:stream.write(text)
    return target

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-dir');args=parser.parse_args()
    try:
        source=Path(args.run_dir).expanduser() if args.run_dir else choose_run(Path.home()/'cf2018_directory_config_runs')
        print('SUMMARY:',write_summary(source,Path.home()/'storage'/'downloads'))
    except (OSError,ValueError):raise SystemExit('Summary not written: saved metadata missing, changed, symlinked or outside read limits. No game/server started.')
if __name__=='__main__':main()
