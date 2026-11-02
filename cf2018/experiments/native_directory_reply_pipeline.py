"""Segmented original receive -> RPC header -> result parse on synthetic wire.

No live socket or complete Android/MsgBuffer/std::function execution claimed.
"""
from native_control import NativeControl,CTX,BUF,OUT,AUX

def probe(library,wire):
 if type(wire) is not bytes or not 32<=len(wire)<=1024:raise ValueError('bounded synthetic wire required')
 n=NativeControl(library);n.write(CTX+4,42);n.write(CTX+0x70c,65536);n.write(CTX+0x714,len(wire));n.uc.mem_write(BUF,wire)
 # Remove execution hooks between stages; no original code is changed.
 def execute(entry,args,stubs):
  old=n.uc.hook_add;handles=[]
  def add(*a,**k):
   h=old(*a,**k);handles.append(h);return h
  n.uc.hook_add=add
  try:return n.execute(entry,args,stubs)
  finally:
   n.uc.hook_add=old
   for h in handles:n.uc.hook_del(h)
 rc=execute(0x3abe34,(CTX,AUX,0),{0x284fcc:('no socket/no additional bytes',-3)})
 if rc:return {'transport_return':rc}
 data=bytes(n.uc.mem_read(OUT,n.read(AUX)));proto=AUX+0x100;name=AUX+0x200;kind=AUX+0x220;seq=AUX+0x230;obj=AUX+0x1000;presult=AUX+0x1100
 n.write(proto,0x4f4768);n.write(proto+0x10,64);n.write(proto+0x14,AUX+0x300);n.write(presult+4,obj)
 cursor=[0];heap=[AUX+0x4000]
 def alloc(size,*_):
  if not 0<size<=4096:raise ValueError('heap allocation bound')
  p=heap[0];heap[0]+=(size+15)&~15
  if heap[0]>=CTX+0x40000:raise ValueError('heap budget')
  return p
 def read(t,dest,count,*_):
  if t!=AUX+0x300 or not 0<=count<=1024 or cursor[0]+count>len(data):raise ValueError('synthetic transport truncation')
  if count:n.uc.mem_write(dest,data[cursor[0]:cursor[0]+count])
  cursor[0]+=count;return count
 def string(protocol,dest,count,*_):
  if not 0<=count<=1024:raise ValueError('string bound')
  p=alloc(count+16)+12
  if count:read(AUX+0x300,p,count)
  n.write(dest,p);n.write(p-12,count);n.write(p-8,count);n.write(p-4,0);n.write(p+count,0,1);return count
 stubs={0x398df4:('bounded memory read',read),0x398182:('bounded memory read',read),0x39c6a4:('bounded GNU string read/storage',string),0x3f8a20:('string destructor boundary',0),0x193e00:('bounded strlen',lambda p,*_:len(bytes(n.uc.mem_read(p,1024)).split(b'\0',1)[0])),0x3c93fc:('bounded synthetic allocator',alloc),0x3c9bec:('free boundary',0)}
 header=execute(0x39c78c,(proto,name,kind,seq),stubs)
 parsed_seq=n.read(seq,8);parsed_kind=n.read(kind);p=n.read(name);parsed_name=bytes(n.uc.mem_read(p,n.read(p-12)))
 result=execute(0x36a860,(presult,proto),stubs)
 begin=n.read(obj+0xc);end=n.read(obj+0x10);trees=(end-begin)//28
 node=b''
 if trees==1:
  p=n.read(begin+8);count=n.read(p-12)
  if count>1024:raise ValueError('decoded node bound')
  node=bytes(n.uc.mem_read(p,count))
 return {'transport_return':rc,'rpc_header_return':header,'result_return':result,'rpc_sequence':parsed_seq,'message_type':parsed_kind,'method':parsed_name,'success_present':bool(n.read(presult+8,1)&1),'result':n.read(obj+4),'trees':trees,'node_count':n.read(begin+4) if trees==1 else 0,'node':node,'consumed':cursor[0],'payload_length':len(data),'stubs':n.calls}
