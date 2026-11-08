"""Bounded local DNS/TLS transport control. No game/account reply or payload log."""
import collections,hashlib,ipaddress,json,socket,socketserver,ssl,struct,threading

SENTINEL='198.18.0.18'
CONFIG_HASHES=frozenset({
 '343bca6e1806f447beb7f69f782ebc61f5fc51bfeb7cc80623160853098a413f',
 'c9bd0b5ed80e90ce9ea695ffe00d9337cb86624d4fd2630a04ff257f91276c15',
 'dca2d537d9d44611edc2d220718f125f4c6bc2bfdd2d333a2235ae886e40fddd'})
REDIRECTOR_SHA='5952e71ae61d868028f688769eee00e4d10676e9ab66de85dad81e251f617e2a'

def canonical(host):return host.lower().rstrip('.')

def scope_from_extensions(text):
    rows=[r for r in text.splitlines() if r.startswith('subjectAltName=')]
    if len(rows)!=1:raise ValueError('One private certificate scope required.')
    values=rows[0].split('=',1)[1].split(',')
    if len(values)!=1 or not values[0].startswith('DNS:'):raise ValueError('Exactly one configuration hostname required.')
    host=canonical(values[0][4:])
    if hashlib.sha256(host.encode('ascii')).hexdigest() not in CONFIG_HASHES:
        raise ValueError('Configuration-only original hostname required.')
    return host

def is_config_target(host,port,scope):
    return port==443 and (host==SENTINEL or canonical(host)==scope)

def patch_redirector(text,scope,tls_port=8443):
    if hashlib.sha256(text.encode()).hexdigest()!=REDIRECTOR_SHA:raise ValueError('Pinned redirector required.')
    if not 1024<=tls_port<=65535:raise ValueError('Unprivileged local TLS port required.')
    anchor='            if is_game_target(host,port):\n'
    if text.count(anchor)!=1:raise ValueError('Redirector gate changed.')
    gate=("            if port == 443 and (host == '198.18.0.18' or host.lower().rstrip('.') == "+repr(scope)+"):\n"
          "                await self.forward(cid,host,port,reader,writer,'127.0.0.1',"+str(tls_port)+",'SCOPED_CONFIG_TLS')\n"
          '            elif is_game_target(host,port):\n')
    out=text.replace(anchor,gate,1);compile(out,'private scoped redirector','exec');return out

def dns_question(packet):
    if not 12<=len(packet)<=4096:raise ValueError('DNS bound')
    ident,flags,qd,an,ns,ar=struct.unpack_from('!6H',packet)
    if flags&0xf800 or qd!=1:raise ValueError('Standard one-question query required')
    p=12;labels=[]
    for _ in range(128):
        if p>=len(packet):raise ValueError('Short question')
        n=packet[p];p+=1
        if n==0:break
        if n>63 or p+n>len(packet):raise ValueError('Compressed/short question')
        labels.append(packet[p:p+n].decode('ascii'));p+=n
    else:raise ValueError('Name budget')
    if p+4>len(packet):raise ValueError('Short question type')
    name=canonical('.'.join(labels))
    if not name or len(name)>253:raise ValueError('Name budget')
    kind,cls=struct.unpack_from('!HH',packet,p)
    return ident,flags,name,kind,cls,p+4

def local_dns_answer(packet,scope):
    try:ident,flags,name,kind,cls,end=dns_question(packet)
    except (ValueError,UnicodeError,struct.error):return None
    if name!=scope or cls!=1 or kind not in (1,28):return None
    answer=(b'\xc0\x0c'+struct.pack('!HHIH',1,1,0,4)+socket.inet_aton(SENTINEL)) if kind==1 else b''
    return struct.pack('!6H',ident,0x8480|(flags&0x0100),1,int(kind==1),0,0)+packet[12:end]+answer

class Counts:
    def __init__(self):self.lock=threading.Lock();self.values=collections.Counter();self.stop=threading.Event()
    def add(self,key):
        with self.lock:self.values[key]+=1
    def take(self,key,limit):
        with self.lock:
            if self.values[key]>=limit:
                self.values['BUDGET_EXHAUSTED']+=1;self.stop.set();return False
            self.values[key]+=1;return True
    def snapshot(self):
        with self.lock:return dict(sorted(self.values.items()))

class DnsRelay:
    def __init__(self,scope,counts,upstream=('1.1.1.1',53)):
        self.scope,self.counts,self.upstream=scope,counts,upstream
    def reply(self,packet,tcp=False):
        if not self.counts.take('DNS_REQUESTS',64):return None
        if not 12<=len(packet)<=4096:self.counts.add('DNS_INVALID_SIZE');return None
        local=local_dns_answer(packet,self.scope)
        if local is not None:
            if not self.counts.take('CONFIG_DNS_OVERRIDES',8):return None
            self.counts.add('CONFIG_A' if struct.unpack_from('!H',local,6)[0] else 'CONFIG_AAAA_EMPTY')
            return local
        self.counts.add('DNS_PASSTHROUGH')
        try:
            if tcp:
                with socket.create_connection(self.upstream,timeout=3) as s:
                    s.sendall(struct.pack('!H',len(packet))+packet)
                    size=struct.unpack('!H',read_exact(s,2))[0]
                    if not 12<=size<=4096:raise ValueError('upstream bound')
                    answer=read_exact(s,size)
            else:
                with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
                    s.settimeout(3);s.connect(self.upstream);s.send(packet);answer=s.recv(4097)
            if not 12<=len(answer)<=4096 or answer[:2]!=packet[:2] or not(answer[2]&0x80):
                raise ValueError('upstream response mismatch')
            return answer
        except (OSError,ValueError,struct.error):self.counts.add('DNS_UPSTREAM_ERROR');return None

def read_exact(s,n):
    out=bytearray()
    while len(out)<n:
        part=s.recv(n-len(out))
        if not part:raise ValueError('short stream')
        out+=part
    return bytes(out)

class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data,s=self.request;reply=self.server.relay.reply(data)
        if reply is not None:s.sendto(reply,self.client_address)

class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(4)
        try:
            n=struct.unpack('!H',read_exact(self.request,2))[0]
            if not 12<=n<=4096:return
            reply=self.server.relay.reply(read_exact(self.request,n),tcp=True)
            if reply is not None:self.request.sendall(struct.pack('!H',len(reply))+reply)
        except (OSError,ValueError,struct.error):self.server.relay.counts.add('DNS_TCP_ERROR')

class WorkerLimit:
    def __init__(self,*args,**kwargs):
        self._workers=threading.BoundedSemaphore(16)
        super().__init__(*args,**kwargs)
    def process_request(self,request,address):
        if not self._workers.acquire(blocking=False):
            self.shutdown_request(request);return
        try:super().process_request(request,address)
        except BaseException:self._workers.release();raise
    def process_request_thread(self,request,address):
        try:super().process_request_thread(request,address)
        finally:self._workers.release()

class UDPServer(WorkerLimit,socketserver.ThreadingUDPServer):daemon_threads=False
class TCPServer(WorkerLimit,socketserver.ThreadingTCPServer):
    daemon_threads=False
    allow_reuse_address=True

def tls_context(cert,key,scope,counts):
    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.minimum_version=ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(str(cert),str(key))
    def sni(s,name,context):
        if not name or canonical(name)!=scope:
            counts.add('TLS_WRONG_SNI');return ssl.ALERT_DESCRIPTION_UNRECOGNIZED_NAME
        counts.add('TLS_MATCHED_SNI')
    ctx.set_servername_callback(sni);return ctx

class TLSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        counts=self.server.counts
        if not counts.take('TLS_TCP_CONNECTIONS',4):return
        self.request.settimeout(4)
        try:
            with self.server.context.wrap_socket(self.request,server_side=True) as s:
                counts.add('TLS_HANDSHAKE_COMPLETE');s.settimeout(2)
                try:
                    if s.recv(1):counts.add('TLS_APPLICATION_BYTE_SEEN')
                except (OSError,ValueError):counts.add('TLS_POST_HANDSHAKE_IO_ERROR')
                # No HTTP/config success reply or request payload is recorded.
        except ssl.SSLError as error:
            if error.reason in ('TLSV1_ALERT_UNKNOWN_CA','SSLV3_ALERT_CERTIFICATE_UNKNOWN','SSLV3_ALERT_BAD_CERTIFICATE'):
                counts.add('TLS_CLIENT_CERTIFICATE_ALERT')
            else:counts.add('TLS_SSL_ERROR')
        except (OSError,ValueError):counts.add('TLS_TRANSPORT_ERROR')
