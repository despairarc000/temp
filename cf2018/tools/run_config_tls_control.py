#!/usr/bin/env python3
"""Local configuration DNS/TLS control; no installation or account reply.

PCAPdroid must capture CrossFire only, exclude Termux, and map UDP/TCP53 to
127.0.0.1:5353 during this test. Disable these mappings when the test ends.
"""
import argparse,datetime,hashlib,ipaddress,json,os,shutil,signal,socket,subprocess,sys,threading,time,uuid
from pathlib import Path

def stop_group(proc):
    for sig,seconds in [(signal.SIGINT,5),(signal.SIGTERM,3),(signal.SIGKILL,2)]:
        try:os.killpg(proc.pid,sig)
        except ProcessLookupError:pass
        try:proc.wait(timeout=seconds);return
        except subprocess.TimeoutExpired:continue
    raise ValueError('Startup process-group shutdown incomplete.')

def execute(args):
    core={};exec(CORE_SOURCE,core)
    prepared=args.prepared_run.resolve();startup=args.startup.resolve()
    try:host=core['scope_from_extensions']((prepared/'private-server-extensions.cnf').read_text())
    except OSError:raise ValueError('Private certificate scope missing; check --prepared-run.') from None
    try:redirector=(startup/'cf2018_redirector.py').read_text()
    except OSError:raise ValueError('Prepared redirector missing; check --startup.') from None
    patched=core['patch_redirector'](redirector,host)
    try:probe=(startup/'routed_probe_r037.py').read_text()
    except OSError:raise ValueError('Prepared startup script missing; check --startup.') from None
    if 'CF2018_VERSION_REPLY' not in probe or 'MAX_SLOTS=12' not in probe:
        raise ValueError('Prepared reviewed version-reply startup folder required.')
    library=Path(os.environ.get('CF18_APOLLO_LIBRARY',''))
    if not library.is_file() or hashlib.sha256(library.read_bytes()).hexdigest()!='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8':
        raise ValueError('Set CF18_APOLLO_LIBRARY to the exact original Apollo first.')
    try:address=ipaddress.ip_address(args.upstream_dns)
    except ValueError:raise ValueError('Public IPv4 upstream DNS required.') from None
    if address.version!=4 or not address.is_global:raise ValueError('Public IPv4 upstream DNS required.')
    if not args.report_dir.is_dir():raise ValueError('Existing report directory required.')
    counts=core['Counts']()
    which='wrong-server' if args.wrong_ca else 'local-server'
    try:context=core['tls_context'](prepared/(which+'.pem'),prepared/(which+'.key.pem'),host,counts)
    except OSError:raise ValueError('Private TLS certificate/key missing or invalid; keep the original preparation folder.') from None
    checks=[]
    try:
        for kind,port in [(socket.SOCK_DGRAM,5353),(socket.SOCK_STREAM,5353),(socket.SOCK_STREAM,8443),
                          (socket.SOCK_STREAM,1080),(socket.SOCK_STREAM,8080),(socket.SOCK_STREAM,8085)]:
            s=socket.socket(socket.AF_INET,kind);checks.append(s)
            if kind==socket.SOCK_STREAM:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            s.bind(('127.0.0.1',port))
    except OSError:raise ValueError('A local test port is busy; stop older probes first.') from None
    finally:
        for s in checks:s.close()
    if args.check:
        print('PREFLIGHT PASS: private scope/certificate/startup/library/ports checked; no listeners or game started.')
        return 0
    if not args.live_opt_in or os.environ.get('CF2018_CONFIG_TLS_TEST')!='YES':
        raise ValueError('Explicit --live-opt-in and CF2018_CONFIG_TLS_TEST=YES required; use --check otherwise.')
    if any(os.environ.get(k)!='YES' for k in ['CF2018_R037_LIVE_REPLY','CF2018_VERSION_REPLY']):
        raise ValueError('Existing startup reply opt-in flags required.')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:8]
    root=args.private_root.resolve()/stamp;root.mkdir(mode=0o700,parents=True,exist_ok=False)
    copy=root/'startup';copy.mkdir(mode=0o700)
    for p in startup.iterdir():
        if p.is_file():shutil.copyfile(p,copy/p.name)
    (copy/'cf2018_redirector.py').write_text(patched)
    relay=core['DnsRelay'](host,counts,(str(address),53))
    servers=[];serving=False;proc=None;stop='ERROR';started=time.monotonic()
    try:
        udp=core['UDPServer'](('127.0.0.1',5353),core['UDPHandler']);udp.relay=relay;servers.append(udp)
        tcp=core['TCPServer'](('127.0.0.1',5353),core['DNSHandler']);tcp.relay=relay;servers.append(tcp)
        tls=core['TCPServer'](('127.0.0.1',8443),core['TLSHandler']);tls.context=context;tls.counts=counts;servers.append(tls)
        for server in servers:threading.Thread(target=server.serve_forever,daemon=True).start()
        serving=True
        proc=subprocess.Popen([sys.executable,str(copy/'routed_probe_r037.py'),'--live-opt-in'],cwd=copy,start_new_session=True)
        print('LOCAL CONFIG TLS CONTROL READY. Start the game; do not tap Google/Facebook.',flush=True)
        print('At end, disable PCAPdroid DNS port mappings. Report contains fixed counters only.',flush=True)
        while time.monotonic()-started<args.seconds:
            if counts.stop.is_set():stop='BUDGET_EXHAUSTED';break
            if proc.poll() is not None:stop='STARTUP_EXITED';break
            time.sleep(.1)
        else:stop='WINDOW_ELAPSED'
    except KeyboardInterrupt:stop='MANUAL_STOP'
    finally:
        if proc:
            try:stop_group(proc)
            except (ValueError,OSError):counts.add('STARTUP_CLEANUP_ERROR')
        for server in servers:
            if serving:server.shutdown()
            server.server_close()
        result={'format':'CF2018_CONFIG_TLS_CONTROL','certificate_mode':'WRONG_CA' if args.wrong_ca else 'LOCAL_CA',
                'operator_apk_label':args.label,'apk_identity_verified':False,
                'stop':stop,'elapsed_seconds':round(time.monotonic()-started,2),'counts':counts.snapshot(),
                'scope':'ONE_ORIGINAL_CONFIG_HOST','http_reply_sent':False,'login_acceptance':'NOT_ESTABLISHED',
                'limits':'Handshake/error counters require DNS/routing context; no configuration/account acceptance implied.'}
        report=args.report_dir/('CF2018_CONFIG_TLS_'+stamp+'.txt')
        with report.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
        print('REPORT: '+str(report));print('Remove/disable the two DNS mappings added for this test now.',flush=True)
    return 0

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--startup',type=Path,required=True)
    p.add_argument('--prepared-run',type=Path,required=True)
    p.add_argument('--upstream-dns',default='1.1.1.1')
    p.add_argument('--seconds',type=int,default=180)
    p.add_argument('--check',action='store_true')
    p.add_argument('--live-opt-in',action='store_true')
    p.add_argument('--wrong-ca',action='store_true')
    p.add_argument('--label',choices=['signature-control','scoped-trust'],default='signature-control')
    p.add_argument('--private-root',type=Path,default=Path.home()/'cf2018_config_tls_runs')
    p.add_argument('--report-dir',type=Path,default=Path.home()/'storage/downloads')
    args=p.parse_args();os.umask(0o077)
    if not 30<=args.seconds<=180:p.error('duration must be30..180 seconds')
    try:return execute(args)
    except ValueError as error:
        print('STOPPED: '+str(error),file=sys.stderr)
        return 1
    except (OSError,KeyError):
        print('Preflight/startup file or socket operation failed; no raw errors exported.',file=sys.stderr)
        return 1

CORE_SOURCE='"""Bounded local DNS/TLS transport control. No game/account reply or payload log."""\nimport collections,hashlib,ipaddress,json,socket,socketserver,ssl,struct,threading\n\nSENTINEL=\'198.18.0.18\'\nCONFIG_HASHES=frozenset({\n \'343bca6e1806f447beb7f69f782ebc61f5fc51bfeb7cc80623160853098a413f\',\n \'c9bd0b5ed80e90ce9ea695ffe00d9337cb86624d4fd2630a04ff257f91276c15\',\n \'dca2d537d9d44611edc2d220718f125f4c6bc2bfdd2d333a2235ae886e40fddd\'})\nREDIRECTOR_SHA=\'5952e71ae61d868028f688769eee00e4d10676e9ab66de85dad81e251f617e2a\'\n\ndef canonical(host):return host.lower().rstrip(\'.\')\n\ndef scope_from_extensions(text):\n    rows=[r for r in text.splitlines() if r.startswith(\'subjectAltName=\')]\n    if len(rows)!=1:raise ValueError(\'One private certificate scope required.\')\n    values=rows[0].split(\'=\',1)[1].split(\',\')\n    if len(values)!=1 or not values[0].startswith(\'DNS:\'):raise ValueError(\'Exactly one configuration hostname required.\')\n    host=canonical(values[0][4:])\n    if hashlib.sha256(host.encode(\'ascii\')).hexdigest() not in CONFIG_HASHES:\n        raise ValueError(\'Configuration-only original hostname required.\')\n    return host\n\ndef is_config_target(host,port,scope):\n    return port==443 and (host==SENTINEL or canonical(host)==scope)\n\ndef patch_redirector(text,scope,tls_port=8443):\n    if hashlib.sha256(text.encode()).hexdigest()!=REDIRECTOR_SHA:raise ValueError(\'Pinned redirector required.\')\n    if not 1024<=tls_port<=65535:raise ValueError(\'Unprivileged local TLS port required.\')\n    anchor=\'            if is_game_target(host,port):\\n\'\n    if text.count(anchor)!=1:raise ValueError(\'Redirector gate changed.\')\n    gate=("            if port == 443 and (host == \'198.18.0.18\' or host.lower().rstrip(\'.\') == "+repr(scope)+"):\\n"\n          "                await self.forward(cid,host,port,reader,writer,\'127.0.0.1\',"+str(tls_port)+",\'SCOPED_CONFIG_TLS\')\\n"\n          \'            elif is_game_target(host,port):\\n\')\n    out=text.replace(anchor,gate,1);compile(out,\'private scoped redirector\',\'exec\');return out\n\ndef dns_question(packet):\n    if not 12<=len(packet)<=4096:raise ValueError(\'DNS bound\')\n    ident,flags,qd,an,ns,ar=struct.unpack_from(\'!6H\',packet)\n    if flags&0xf800 or qd!=1:raise ValueError(\'Standard one-question query required\')\n    p=12;labels=[]\n    for _ in range(128):\n        if p>=len(packet):raise ValueError(\'Short question\')\n        n=packet[p];p+=1\n        if n==0:break\n        if n>63 or p+n>len(packet):raise ValueError(\'Compressed/short question\')\n        labels.append(packet[p:p+n].decode(\'ascii\'));p+=n\n    else:raise ValueError(\'Name budget\')\n    if p+4>len(packet):raise ValueError(\'Short question type\')\n    name=canonical(\'.\'.join(labels))\n    if not name or len(name)>253:raise ValueError(\'Name budget\')\n    kind,cls=struct.unpack_from(\'!HH\',packet,p)\n    return ident,flags,name,kind,cls,p+4\n\ndef local_dns_answer(packet,scope):\n    try:ident,flags,name,kind,cls,end=dns_question(packet)\n    except (ValueError,UnicodeError,struct.error):return None\n    if name!=scope or cls!=1 or kind not in (1,28):return None\n    answer=(b\'\\xc0\\x0c\'+struct.pack(\'!HHIH\',1,1,0,4)+socket.inet_aton(SENTINEL)) if kind==1 else b\'\'\n    return struct.pack(\'!6H\',ident,0x8480|(flags&0x0100),1,int(kind==1),0,0)+packet[12:end]+answer\n\nclass Counts:\n    def __init__(self):self.lock=threading.Lock();self.values=collections.Counter();self.stop=threading.Event()\n    def add(self,key):\n        with self.lock:self.values[key]+=1\n    def take(self,key,limit):\n        with self.lock:\n            if self.values[key]>=limit:\n                self.values[\'BUDGET_EXHAUSTED\']+=1;self.stop.set();return False\n            self.values[key]+=1;return True\n    def snapshot(self):\n        with self.lock:return dict(sorted(self.values.items()))\n\nclass DnsRelay:\n    def __init__(self,scope,counts,upstream=(\'1.1.1.1\',53)):\n        self.scope,self.counts,self.upstream=scope,counts,upstream\n    def reply(self,packet,tcp=False):\n        if not self.counts.take(\'DNS_REQUESTS\',64):return None\n        if not 12<=len(packet)<=4096:self.counts.add(\'DNS_INVALID_SIZE\');return None\n        local=local_dns_answer(packet,self.scope)\n        if local is not None:\n            if not self.counts.take(\'CONFIG_DNS_OVERRIDES\',8):return None\n            self.counts.add(\'CONFIG_A\' if struct.unpack_from(\'!H\',local,6)[0] else \'CONFIG_AAAA_EMPTY\')\n            return local\n        self.counts.add(\'DNS_PASSTHROUGH\')\n        try:\n            if tcp:\n                with socket.create_connection(self.upstream,timeout=3) as s:\n                    s.sendall(struct.pack(\'!H\',len(packet))+packet)\n                    size=struct.unpack(\'!H\',read_exact(s,2))[0]\n                    if not 12<=size<=4096:raise ValueError(\'upstream bound\')\n                    answer=read_exact(s,size)\n            else:\n                with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:\n                    s.settimeout(3);s.connect(self.upstream);s.send(packet);answer=s.recv(4097)\n            if not 12<=len(answer)<=4096 or answer[:2]!=packet[:2] or not(answer[2]&0x80):\n                raise ValueError(\'upstream response mismatch\')\n            return answer\n        except (OSError,ValueError,struct.error):self.counts.add(\'DNS_UPSTREAM_ERROR\');return None\n\ndef read_exact(s,n):\n    out=bytearray()\n    while len(out)<n:\n        part=s.recv(n-len(out))\n        if not part:raise ValueError(\'short stream\')\n        out+=part\n    return bytes(out)\n\nclass UDPHandler(socketserver.BaseRequestHandler):\n    def handle(self):\n        data,s=self.request;reply=self.server.relay.reply(data)\n        if reply is not None:s.sendto(reply,self.client_address)\n\nclass DNSHandler(socketserver.BaseRequestHandler):\n    def handle(self):\n        self.request.settimeout(4)\n        try:\n            n=struct.unpack(\'!H\',read_exact(self.request,2))[0]\n            if not 12<=n<=4096:return\n            reply=self.server.relay.reply(read_exact(self.request,n),tcp=True)\n            if reply is not None:self.request.sendall(struct.pack(\'!H\',len(reply))+reply)\n        except (OSError,ValueError,struct.error):self.server.relay.counts.add(\'DNS_TCP_ERROR\')\n\nclass WorkerLimit:\n    def __init__(self,*args,**kwargs):\n        self._workers=threading.BoundedSemaphore(16)\n        super().__init__(*args,**kwargs)\n    def process_request(self,request,address):\n        if not self._workers.acquire(blocking=False):\n            self.shutdown_request(request);return\n        try:super().process_request(request,address)\n        except BaseException:self._workers.release();raise\n    def process_request_thread(self,request,address):\n        try:super().process_request_thread(request,address)\n        finally:self._workers.release()\n\nclass UDPServer(WorkerLimit,socketserver.ThreadingUDPServer):daemon_threads=False\nclass TCPServer(WorkerLimit,socketserver.ThreadingTCPServer):\n    daemon_threads=False\n    allow_reuse_address=True\n\ndef tls_context(cert,key,scope,counts):\n    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.minimum_version=ssl.TLSVersion.TLSv1_2\n    ctx.load_cert_chain(str(cert),str(key))\n    def sni(s,name,context):\n        if not name or canonical(name)!=scope:\n            counts.add(\'TLS_WRONG_SNI\');return ssl.ALERT_DESCRIPTION_UNRECOGNIZED_NAME\n        counts.add(\'TLS_MATCHED_SNI\')\n    ctx.set_servername_callback(sni);return ctx\n\nclass TLSHandler(socketserver.BaseRequestHandler):\n    def handle(self):\n        counts=self.server.counts\n        if not counts.take(\'TLS_TCP_CONNECTIONS\',4):return\n        self.request.settimeout(4)\n        try:\n            with self.server.context.wrap_socket(self.request,server_side=True) as s:\n                counts.add(\'TLS_HANDSHAKE_COMPLETE\');s.settimeout(2)\n                try:\n                    if s.recv(1):counts.add(\'TLS_APPLICATION_BYTE_SEEN\')\n                except (OSError,ValueError):counts.add(\'TLS_POST_HANDSHAKE_IO_ERROR\')\n                # No HTTP/config success reply or request payload is recorded.\n        except ssl.SSLError as error:\n            if error.reason in (\'TLSV1_ALERT_UNKNOWN_CA\',\'SSLV3_ALERT_CERTIFICATE_UNKNOWN\',\'SSLV3_ALERT_BAD_CERTIFICATE\'):\n                counts.add(\'TLS_CLIENT_CERTIFICATE_ALERT\')\n            else:counts.add(\'TLS_SSL_ERROR\')\n        except (OSError,ValueError):counts.add(\'TLS_TRANSPORT_ERROR\')\n'
if __name__=='__main__':sys.exit(main())
