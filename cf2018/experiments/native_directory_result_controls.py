"""Original generated directory result writer/reader on synthetic configuration.

No socket, whole RPC dispatcher, authenticated account or managed/UI execution.
"""
from native_control import NativeControl,CTX,BUF,AUX
from native_directory_node_controls import pack

def component(library,include=True):
 node,_=pack(library,0,0x01010100)
 n=NativeControl(library);proto=AUX+0x100;obj=AUX+0x1000;tree=AUX+0x2000
 n.write(proto,0x4f4768);n.write(proto+0x10,64);n.write(proto+0x14,AUX+0x300)
 n.write(obj+0x20,int(include),1);n.write(obj+0xc,BUF+0x300);n.write(BUF+0x300-12,0)
 n.write(obj+0x10,tree);n.write(obj+0x14,tree+28);n.write(obj+0x18,tree+28)
 n.write(tree+4,1);n.write(tree+8,BUF+0x100);n.write(BUF+0x100-12,len(node));n.uc.mem_write(BUF+0x100,node)
 chunks=[]
 def sink(t,p,c,*_):
  if t!=AUX+0x300 or c>2048:raise ValueError('memory sink bound')
  chunks.append(bytes(n.uc.mem_read(p,c)));return 0
 rc=n.execute(0x369f28,(obj,proto),{0x398ede:('bounded memory writer',sink)})
 return b''.join(chunks),rc,n.calls

def read_component(library,wire,pointer=False):
 if type(wire) is not bytes or not 0<len(wire)<=2048:raise ValueError('synthetic component bound')
 n=NativeControl(library);proto=AUX+0x100;obj=AUX+0x1000;presult=AUX+0x1100;target=obj+4
 n.write(proto,0x4f4768);n.write(proto+0x10,64);n.write(proto+0x14,AUX+0x300);n.write(presult+4,target)
 cursor=[0];heap=[AUX+0x4000]
 def allocate(size,*_):
  if not 0<size<=4096:raise ValueError('allocation bound')
  addr=heap[0];heap[0]+=(size+15)&~15
  if heap[0]>=CTX+0x40000:raise ValueError('heap budget')
  return addr
 def read(t,dest,count,*_):
  if t!=AUX+0x300 or not 0<=count<=1024 or cursor[0]+count>len(wire):raise ValueError('bounded synthetic truncation')
  if count:n.uc.mem_write(dest,wire[cursor[0]:cursor[0]+count])
  cursor[0]+=count;return count
 def string(proto,dest,count,*_):
  if not 0<=count<=1024:raise ValueError('string length bound')
  ptr=allocate(count+16)+12
  if count:read(AUX+0x300,ptr,count)
  n.write(dest,ptr);n.write(ptr-12,count);n.write(ptr-8,count);n.write(ptr-4,0);n.write(ptr+count,0,1)
  return count
 def strlen(ptr,*_):return len(bytes(n.uc.mem_read(ptr,1024)).split(b'\0',1)[0])
 stubs={0x3c93fc:('bounded allocation',allocate),0x3c9bec:('free boundary',0),0x193e00:('bounded strlen',strlen),0x398df4:('bounded memory reader',read),0x398182:('bounded memory reader',read),0x39c6a4:('bounded GNU string read/storage',string),0x3f8a20:('string destructor boundary',0)}
 rc=n.execute(0x36a860 if pointer else 0x36a7a4,(presult if pointer else obj,proto),stubs)
 presence=n.read(presult+8 if pointer else obj+0x20,1)&1
 begin=n.read(target+0xc);end=n.read(target+0x10);trees=(end-begin)//28 if end>=begin else -1
 node=b''
 if presence and trees==1:
  ptr=n.read(begin+8);length=n.read(ptr-12)
  if length>1024:raise ValueError('decoded node bound')
  node=bytes(n.uc.mem_read(ptr,length))
 return {'return':rc,'consumed':cursor[0],'success_present':bool(presence),'result':n.read(target+4),'trees':trees,'node_count':n.read(begin+4) if trees==1 else 0,'node':node,'stubs':n.calls}
