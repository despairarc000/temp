"""Original 64-bit pending lookup; protocol/callback/erase boundaries substituted."""
from native_control import NativeControl,CTX,AUX,STACK,STOP

def probe(library,received,pending=0x100000002):
 if type(received) is not int or not 0<=received<2**64 or type(pending) is not int or not 0<=pending<2**64:raise ValueError('synthetic u64 required')
 n=NativeControl(library);node=AUX+0x1000;shared=AUX+0x100;proto=AUX+0x200;pv=AUX+0x300;trans=AUX+0x400;tv=AUX+0x500
 n.write(CTX+0x58,node);n.write(node+4,CTX+0x54);n.write(node+0x10,pending,8)
 n.write(shared,proto);n.write(proto,pv);n.write(pv+0xb0,STOP+0x101);n.write(pv+0xb4,STOP+0x105);n.write(trans,tv);n.write(tv+0x20,STOP+0x109);n.write(STACK+0xf000,shared)
 calls=[]
 def gettransport(dest,protocol,*_):n.write(dest,trans);n.write(dest+4,0);return dest
 def lookup(tree,key,*_):calls.append(('lookup',n.read(key,8)==pending));return AUX+0x600
 def callback(fun,status,protocol,*_):calls.append(('callback',protocol==proto));return 0
 def erase(tree,key,*_):calls.append(('erase',n.read(key,8)==pending));return 1
 def skipped(*_):calls.append(('skipped',True));return 0
 stubs={0x3c34d8:('callback map-value access boundary',lookup),0x3c27a4:('typed callback boundary',callback),0x3c2e70:('map erase boundary',erase),STOP+0x100:('protocol skip boundary',skipped),STOP+0x104:('protocol transport access boundary',gettransport),STOP+0x108:('transport read-end boundary',0),0x33da52:('protocol message-end boundary',0),0x33e286:('shared-count release boundary',0)}
 rc=n.execute(0x3c382c,(CTX,2,received&0xffffffff,received>>32),stubs)
 return {'return':rc,'events':calls,'stubs':n.calls}
