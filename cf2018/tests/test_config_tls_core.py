import asyncio,contextlib,hashlib,importlib.util,json,os,socket,ssl,struct,sys,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'experiments'))
import config_tls_core as c

def question(name='synthetic.invalid',kind=1,ident=123):
    return struct.pack('!6H',ident,0x100,1,0,0,0)+b''.join(bytes([len(x)])+x.encode() for x in name.split('.'))+b'\0'+struct.pack('!HH',kind,1)

class DNS(unittest.TestCase):
    def test_a_reply_and_aaaa_empty_preserve_question(self):
        for kind,count in [(1,1),(28,0)]:
            packet=question(kind=kind);reply=c.local_dns_answer(packet,'synthetic.invalid')
            self.assertEqual(reply[:2],packet[:2]);self.assertEqual(struct.unpack_from('!H',reply,6)[0],count)
            self.assertEqual(reply[12:len(packet)],packet[12:])
            if kind==1:self.assertEqual(socket.inet_ntoa(reply[-4:]),c.SENTINEL)

    def test_other_host_type_and_malformed_query_are_not_overridden(self):
        for p in [question('other.invalid'),question(kind=15),b'',question()[:-2],question().replace(b'\x09synthetic',b'\xc0\x0c',1)]:
            self.assertIsNone(c.local_dns_answer(p,'synthetic.invalid'))

    def test_scope_rejects_account_or_arbitrary_host(self):
        with self.assertRaises(ValueError):c.scope_from_extensions('subjectAltName=DNS:synthetic.invalid')
        with patch.object(c,'CONFIG_HASHES',{hashlib.sha256(b'synthetic.invalid').hexdigest()}):
            self.assertEqual(c.scope_from_extensions('subjectAltName=DNS:SYNTHETIC.INVALID.'),'synthetic.invalid')
            with self.assertRaises(ValueError):c.scope_from_extensions('subjectAltName=DNS:synthetic.invalid,DNS:other.invalid')

    def test_only_selected_host_or_synthetic_ip_on_443_is_routed(self):
        self.assertTrue(c.is_config_target(c.SENTINEL,443,'synthetic.invalid'))
        self.assertTrue(c.is_config_target('SYNTHETIC.INVALID.',443,'synthetic.invalid'))
        for host,port in [('other.invalid',443),(c.SENTINEL,80),('127.0.0.1',443)]:
            self.assertFalse(c.is_config_target(host,port,'synthetic.invalid'))

    def test_unrelated_dns_forwarded_byte_for_byte_to_synthetic_upstream(self):
        packet=question('other.invalid');reply=packet[:2]+b'\x81\x80'+packet[4:]
        upstream=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);upstream.bind(('127.0.0.1',0));upstream.settimeout(2)
        seen=[]
        def serve():
            p,peer=upstream.recvfrom(4096);seen.append(p);upstream.sendto(reply,peer)
        t=threading.Thread(target=serve);t.start()
        try:
            relay=c.DnsRelay('synthetic.invalid',c.Counts(),upstream.getsockname())
            self.assertEqual(relay.reply(packet),reply)
        finally:t.join(3);upstream.close()
        self.assertEqual(seen,[packet])

    def test_dns_budget_is_finite(self):
        counts=c.Counts();relay=c.DnsRelay('synthetic.invalid',counts)
        for _ in range(8):self.assertIsNotNone(relay.reply(question()))
        self.assertIsNone(relay.reply(question()));self.assertTrue(counts.stop.is_set())

    def test_udp_and_tcp_local_query_servers(self):
        counts=c.Counts();relay=c.DnsRelay('synthetic.invalid',counts);servers=[]
        try:
            for server,handler in [(c.UDPServer,c.UDPHandler),(c.TCPServer,c.DNSHandler)]:
                s=server(('127.0.0.1',0),handler);s.relay=relay;servers.append(s)
                threading.Thread(target=s.serve_forever,daemon=True).start()
            packet=question()
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
                s.settimeout(2);s.sendto(packet,servers[0].server_address);reply,_=s.recvfrom(4096)
                self.assertEqual(reply,c.local_dns_answer(packet,'synthetic.invalid'))
            with socket.create_connection(servers[1].server_address,timeout=2) as s:
                s.sendall(struct.pack('!H',len(packet))+packet);n=struct.unpack('!H',c.read_exact(s,2))[0]
                self.assertEqual(c.read_exact(s,n),reply)
        finally:
            for s in servers:s.shutdown();s.server_close()

class TLS(unittest.TestCase):
    def test_post_handshake_timeout_is_not_certificate_rejection(self):
        from unittest.mock import MagicMock
        from types import SimpleNamespace
        counts=c.Counts();connection=MagicMock();connection.recv.side_effect=TimeoutError()
        context=MagicMock();context.wrap_socket.return_value.__enter__.return_value=connection
        c.TLSHandler(MagicMock(),('127.0.0.1',1),SimpleNamespace(counts=counts,context=context))
        self.assertEqual(counts.snapshot(),{'TLS_TCP_CONNECTIONS':1,'TLS_HANDSHAKE_COMPLETE':1,'TLS_POST_HANDSHAKE_IO_ERROR':1})
    @unittest.skipUnless(importlib.util.find_spec('cryptography'),'optional synthetic certificate generator required')
    def test_synthetic_trust_accept_and_wrong_ca_reject_without_payload_log(self):
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes,serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime,time
        now=datetime.datetime.now(datetime.timezone.utc)
        def cert(name,issuer=None):
            key=rsa.generate_private_key(public_exponent=65537,key_size=2048);dn=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,name)])
            b=x509.CertificateBuilder().subject_name(dn).issuer_name(issuer[1].subject if issuer else dn).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=1)).add_extension(x509.BasicConstraints(ca=issuer is None,path_length=None),critical=True)
            if issuer:b=b.add_extension(x509.SubjectAlternativeName([x509.DNSName('synthetic.invalid')]),False)
            return key,b.sign(issuer[0] if issuer else key,hashes.SHA256())
        ca=cert('synthetic root');wrong=cert('synthetic wrong root');leaf=cert('synthetic leaf',ca)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for name,pair in [('ca',ca),('wrong',wrong),('server',leaf)]:
                (p/(name+'.pem')).write_bytes(pair[1].public_bytes(serialization.Encoding.PEM))
            (p/'key.pem').write_bytes(leaf[0].private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
            counts=c.Counts();server=c.TCPServer(('127.0.0.1',0),c.TLSHandler)
            server.context=c.tls_context(p/'server.pem',p/'key.pem','synthetic.invalid',counts);server.counts=counts
            threading.Thread(target=server.serve_forever,daemon=True).start()
            try:
                good=ssl.create_default_context(cafile=str(p/'ca.pem'))
                with socket.create_connection(server.server_address,timeout=2) as raw:
                    with good.wrap_socket(raw,server_hostname='synthetic.invalid') as s:s.sendall(b'SYNTHETIC_SECRET_NOT_LOGGED');s.recv(1)
                bad=ssl.create_default_context(cafile=str(p/'wrong.pem'))
                with socket.create_connection(server.server_address,timeout=2) as raw:
                    with self.assertRaises(ssl.SSLCertVerificationError):bad.wrap_socket(raw,server_hostname='synthetic.invalid')
                with socket.create_connection(server.server_address,timeout=2) as raw:
                    with self.assertRaises(ssl.SSLError):good.wrap_socket(raw,server_hostname='other.invalid')
                deadline=time.monotonic()+2
                while counts.snapshot().get('TLS_CLIENT_CERTIFICATE_ALERT',0)<1 and time.monotonic()<deadline:time.sleep(.01)
            finally:server.shutdown();server.server_close()
            data=counts.snapshot();self.assertEqual(data['TLS_HANDSHAKE_COMPLETE'],1)
            self.assertEqual(data['TLS_APPLICATION_BYTE_SEEN'],1);self.assertEqual(data['TLS_CLIENT_CERTIFICATE_ALERT'],1)
            self.assertEqual(data['TLS_WRONG_SNI'],1)
            self.assertNotIn('SYNTHETIC_SECRET',json.dumps(data));self.assertNotIn('synthetic.invalid',json.dumps(data))

class Wrapper(unittest.TestCase):
    def runner(self):
        spec=importlib.util.spec_from_file_location('runner',ROOT/'tools/run_config_tls_control.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def test_embedded_source_matches_reviewed_module(self):
        m=self.runner()
        self.assertEqual(m.CORE_SOURCE,(ROOT/'experiments/config_tls_core.py').read_text())
    def test_shutdown_signals_only_child_group_and_waits(self):
        from unittest.mock import Mock
        m=self.runner();proc=Mock(pid=12345)
        with patch.object(m.os,'killpg') as kill:
            m.stop_group(proc)
        kill.assert_called_once_with(12345,m.signal.SIGINT);proc.wait.assert_called_once_with(timeout=5)
    def test_shutdown_escalates_when_group_does_not_stop(self):
        from unittest.mock import Mock
        m=self.runner();proc=Mock(pid=12345)
        proc.wait.side_effect=[m.subprocess.TimeoutExpired('synthetic',5),m.subprocess.TimeoutExpired('synthetic',3),None]
        with patch.object(m.os,'killpg') as kill:m.stop_group(proc)
        self.assertEqual([x.args for x in kill.call_args_list],[(12345,m.signal.SIGINT),(12345,m.signal.SIGTERM),(12345,m.signal.SIGKILL)])

@unittest.skipUnless(os.environ.get('CF18_TLS_FIXTURE') and os.environ.get('CF18_PINNED_STARTUP') and os.environ.get('CF18_APOLLO_LIBRARY'),'explicit private prepared sources and certificate fixture required')
class RunnerIntegration(unittest.TestCase):
    def args(self,root,check=False):
        from types import SimpleNamespace
        return SimpleNamespace(prepared_run=Path(os.environ['CF18_TLS_FIXTURE']),startup=Path(os.environ['CF18_PINNED_STARTUP']),upstream_dns='1.1.1.1',wrong_ca=False,check=check,live_opt_in=True,seconds=30,private_root=root/'private',report_dir=root,label='signature-control')
    def runner(self):
        spec=importlib.util.spec_from_file_location('runner',ROOT/'tools/run_config_tls_control.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def test_preflight_does_not_spawn_startup(self):
        m=self.runner()
        with tempfile.TemporaryDirectory() as tmp,patch.object(m.subprocess,'Popen') as spawn,contextlib.redirect_stdout(__import__('io').StringIO()):
            self.assertEqual(m.execute(self.args(Path(tmp),check=True)),0)
            spawn.assert_not_called();self.assertEqual(list(Path(tmp).iterdir()),[])
    def test_orchestration_closes_listeners_and_reports_without_game_process(self):
        from unittest.mock import Mock
        m=self.runner();proc=Mock(pid=12345);proc.poll.return_value=0
        flags={k:'YES' for k in ['CF2018_R037_LIVE_REPLY','CF2018_VERSION_REPLY','CF2018_CONFIG_TLS_TEST']}
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,flags),patch.object(m.subprocess,'Popen',return_value=proc) as spawn,patch.object(m.os,'killpg') as kill,contextlib.redirect_stdout(__import__('io').StringIO()):
            root=Path(tmp);self.assertEqual(m.execute(self.args(root)),0)
            spawn.assert_called_once();kill.assert_called_once_with(12345,m.signal.SIGINT)
            report=json.loads(next(root.glob('CF2018_CONFIG_TLS_*.txt')).read_text())
            self.assertEqual(report['stop'],'STARTUP_EXITED');self.assertEqual(report['counts'],{})
            self.assertFalse(report['http_reply_sent']);self.assertFalse(report['apk_identity_verified'])
            self.assertNotIn('subjectAltName',json.dumps(report))
            self.assertEqual(m.execute(self.args(root,check=True)),0)

@unittest.skipUnless(os.environ.get('CF18_PINNED_STARTUP'),'explicit pinned private startup source required')
class SocksIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_exact_domain_and_ip_gate_and_other_passthrough(self):
        from types import SimpleNamespace
        source=Path(os.environ['CF18_PINNED_STARTUP'])
        text=(source/'cf2018_redirector.py').read_text()
        async def endpoint(reader,writer):
            writer.write(b'SYNTHETIC_LOCAL');await writer.drain();writer.close();await writer.wait_closed()
        upstream=await asyncio.start_server(endpoint,'127.0.0.1',0)
        port=upstream.sockets[0].getsockname()[1]
        with tempfile.TemporaryDirectory() as tmp:
            patched=c.patch_redirector(text,'synthetic.invalid',port)
            sys.path.insert(0,str(source))
            try:
                namespace={'__name__':'private_redirector_control'};exec(compile(patched,'private redirector','exec'),namespace)
                redirector=namespace['Redirector'](SimpleNamespace(log_dir=tmp,mode='forward',target_only=False,connect_timeout=2,emulator_host='127.0.0.1',emulator_port_8080=port,emulator_port_8085=port))
                proxy=await asyncio.start_server(redirector.handle,'127.0.0.1',0)
                original_open=asyncio.open_connection
                async def loopback_only(host,port,*args,**kwargs):
                    if host!='127.0.0.1':raise AssertionError('External connection forbidden in synthetic test')
                    return await original_open(host,port,*args,**kwargs)
                guard=patch.object(asyncio,'open_connection',side_effect=loopback_only);guard.start()
                try:
                    for host,target_port in [(c.SENTINEL,443),('synthetic.invalid',443),('127.0.0.1',port),('45.113.69.32',8080)]:
                        reader,writer=await asyncio.open_connection('127.0.0.1',proxy.sockets[0].getsockname()[1])
                        writer.write(b'\x05\x01\x00');await writer.drain();self.assertEqual(await reader.readexactly(2),b'\x05\x00')
                        if host=='synthetic.invalid':address=b'\x03'+bytes([len(host)])+host.encode()
                        else:address=b'\x01'+socket.inet_aton(host)
                        writer.write(b'\x05\x01\x00'+address+struct.pack('!H',target_port));await writer.drain()
                        self.assertEqual((await reader.readexactly(10))[1],0)
                        self.assertEqual(await reader.readexactly(15),b'SYNTHETIC_LOCAL')
                        writer.close();await writer.wait_closed()
                    await asyncio.sleep(.05)
                finally:guard.stop();proxy.close();await proxy.wait_closed()
                events=[json.loads(x) for x in (Path(tmp)/'events.jsonl').read_text().splitlines()]
                self.assertEqual([x['status'] for x in events if x['event']=='CONNECTED'],['SCOPED_CONFIG_TLS','SCOPED_CONFIG_TLS','PASSTHROUGH','EMULATOR'])
            finally:sys.path.remove(str(source));upstream.close();await upstream.wait_closed()

if __name__=='__main__':unittest.main()
