"""Actual original binary header/argument writers; synthetic memory sink only.
No full sender, MsgBuffer callback, sockets or phone data executed.
"""
from native_control import NativeControl,AUX,BUF,STACK
METHODS={'all':('DirService:get_server_dirtree_all',0x369c18,3),'by_id':('DirService:get_server_dirtree_by_id',0x369e50,4),'by_ids':('DirService:get_server_by_ids',0x36a0d4,5)}
def build(library,label,length,strict=False):
 if label not in METHODS or type(length) is not int or not 0<=length<=32 or type(strict) is not bool:raise ValueError("bounded synthetic case required")
 method,entry,count=METHODS[label];n=NativeControl(library);protocol=AUX+0x100;name=AUX+0x200;args=AUX+0x400
 n.write(protocol,0x4f4768);n.write(protocol+0x10,64);n.write(protocol+0x14,AUX+0x300);n.write(protocol+0x21,int(strict),1)
 n.write(name,BUF+0x100);n.write(BUF+0x100-12,len(method));n.uc.mem_write(BUF+0x100,method.encode())
 n.write(STACK+0xf000,1);n.write(STACK+0xf004,0)
 chunks=[]
 def sink(t,p,c,_):
  assert t==AUX+0x300 and c<=256
  chunks.append(bytes(n.uc.mem_read(p,c)));return 0
 rc=n.execute(0x39c3bc,(protocol,name,1,0),{0x398ede:('bounded synthetic memory sink',sink)});assert rc>=0
 header=b''.join(chunks)
 z=NativeControl(library);z.uc.mem_write(0x1000000,bytes(n.uc.mem_read(0x1000000,0x40000)));chunks=[]
 for i in range(count):z.write(args+4+4*i,AUX+0x600+0x20*i)
 string=AUX+0x620;z.write(string,BUF+0x200);z.write(BUF+0x200-12,length)
 if length:z.uc.mem_write(BUF+0x200,b'S'*length)
 def sink2(t,p,c,_):
  assert t==AUX+0x300 and c<=256
  chunks.append(bytes(z.uc.mem_read(p,c)));return 0
 rc=z.execute(entry,(args,protocol),{0x398ede:('bounded synthetic memory sink',sink2)});assert rc>=0
 return bytes(4)+header+b''.join(chunks),z.calls
