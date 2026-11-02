"""Original encrypted-ACK receiver controls; synthetic fixtures only.

No sockets, accounts, phone packets or outbound authentication. Source identity
is enforced by NativeControl. Auth-send is suppressed with a probe sentinel.
"""
from native_control import NativeControl,CTX,BUF,OUT,AUX,STACK
from native_syn_ack_handoff import _field,_prepare_syn
from native_auth_rx import _Trace
KEY=bytes(range(16))
def envelope(h):return b'\xaa'+(5+len(h)).to_bytes(4,'big')+h
def encrypt(library,body,method):
 n=NativeControl(library);n.write(CTX+0x11c,method);n.write(CTX+0x458,16,1);n.uc.mem_write(CTX+0x459,KEY);assert n.execute(0x3ab24a,(CTX,))==0
 z=NativeControl(library);z.uc.mem_write(CTX,bytes(n.uc.mem_read(CTX,0x40000)));z.uc.mem_write(BUF,body);z.write(AUX,256);z.write(STACK+0xf000,AUX)
 assert z.execute(0x3ab296,(CTX,BUF,len(body),OUT),{0x193e78:('synthetic deterministic randomness',7)})==0
 return bytes(z.uc.mem_read(OUT,z.read(AUX)))
def run(library, *, method=4,mode=2,encrypted=True,variant='valid'):
 if method not in (0,2,3,4) or mode not in (0,2) or type(encrypted) is not bool or variant not in ('valid','bad_body','bad_cipher_length','wrong_key','bad_extension'):
  raise ValueError('unsupported bounded synthetic case')
 body=envelope(_field(0x1002,5,_field(1,1,0)))
 if variant=='bad_body':body=b'\xa5'+body[1:]
 if encrypted:body=encrypt(library,body,method)
 if variant=='bad_cipher_length':body=body[:-1]
 key=bytes(reversed(KEY)) if variant=='wrong_key' else KEY
 rawkey=_field(1,0,16)+_field(2,5,key)
 info=_field(2,5,rawkey) if mode==2 else b'\x01\x00'
 ack=_field(1,1,method)+_field(2,1,mode)+_field(3,5,info)+_field(4,1,0)+_field(5,0,1024)+_field(6,0,0)
 if variant=='bad_extension':ack=ack[:-1]
 base=b''.join(_field(i,1 if i==6 else 0,v) for i,v in enumerate([0x4366,0,1,0x1002,0,int(encrypted),1,0,len(body)],1))
 wire=envelope(_field(1,5,base)+_field(2,5,_field(0x1002,5,ack)))+body
 n,_=_prepare_syn(library,10,False,'unit_3')
 z=NativeControl(library);z.uc.mem_write(CTX,bytes(n.uc.mem_read(CTX,0x40000)));z.write(CTX+0x70c,65536);z.write(CTX+0x714,len(wire));z.uc.mem_write(BUF,wire)
 trace=_Trace(z)
 from unicorn import UC_HOOK_CODE
 calls=[]
 def observe(u,a,size,_):
  if a in [0x3ab24a,0x3ab31e,0x2845fc,0x3b8860,0x3b49a6]:calls.append(hex(a))
 z.uc.hook_add(UC_HOOK_CODE,observe)
 rc=z.execute(0x3a9f8c,(CTX,0),{0x284fcc:('network no new data/no socket',-3),0x3ab964:('auth send suppressed',-77)})
 return {'return':rc,'auth_boundary':'auth send suppressed' in z.calls,'state':z.read(CTX+0x6c8),'method':z.read(CTX+0x11c),'mode':z.read(CTX+0x120),'key_length':z.read(CTX+0x458,1),'native_calls':calls,'syn_stubs':n.calls,'body_events':[v for v in trace.events if v['stage']=='body_unpack'],'stubs':sorted(set(z.calls))}
