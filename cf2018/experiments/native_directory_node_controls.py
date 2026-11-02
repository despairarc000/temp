"""Synthetic node round trips through original TLV constructors/writers/readers.
No directory reply, callback acceptance, endpoint, account or network operation.
"""
from native_control import NativeControl,CTX,BUF,OUT,AUX,STACK

def pack(library,selector=0):
 if selector not in (0,1):raise ValueError('synthetic category/leaf only')
 obj=AUX+0x1000;n=NativeControl(library);assert n.execute(0x36eb4c,(obj,))==0
 if selector:
  n=copy(library,n);n.write(obj,1,2);assert n.execute(0x36e7f0,(obj+4,0,1,0))==0
 z=copy(library,n);z.write(STACK+0xf000,1)
 def length(ptr,cap,*_):
  if not 0<=cap<=1024:raise ValueError('string bound')
  return len(bytes(z.uc.mem_read(ptr,cap)).split(b'\0',1)[0])
 rc=z.execute(0x36eca6,(obj,BUF,2048,OUT),{0x1941f0:('bounded strnlen',length),0x193e00:('bounded strlen',lambda p,*_:length(p,1024))})
 assert rc==0
 return bytes(z.uc.mem_read(BUF,z.read(OUT))),z.calls

def copy(library,n):
 z=NativeControl(library);z.uc.mem_write(CTX,bytes(n.uc.mem_read(CTX,0x40000)));return z

def unpack(library,wire):
 if type(wire) is not bytes or not 0<len(wire)<=2048:raise ValueError('bounded synthetic bytes only')
 n=NativeControl(library);n.uc.mem_write(BUF,wire)
 rc=n.execute(0x36ef30,(AUX+0x1000,BUF,len(wire),OUT))
 return {'return':rc,'consumed':n.read(OUT),'selector':n.read(AUX+0x1000,2),'stubs':n.calls}

def conversion_probe(library,wire,count=1):
 """Actual CreateTreeNode control; AObject/AString/AArray runtime is substituted.

 This observes parser/loop acceptance, not fully populated UI objects.
 """
 if type(wire) is not bytes or not 0<len(wire)<=2048 or count not in (0,1,2):raise ValueError('bounded synthetic node control required')
 n=NativeControl(library);raw=AUX+0x1000;out=AUX+0x2000
 n.write(raw+4,count);n.write(raw+8,BUF);n.write(BUF-12,len(wire));n.uc.mem_write(BUF,wire);added=[]
 def add(arr,obj,*_):added.append(n.read(obj+0xc));return arr
 rc=n.execute(0x370bf4,(raw,out),{0x36ffcc:('NodeWrapper constructor boundary',lambda obj,*_:obj),0x3707e4:('NodeWrapper destructor boundary',0),0x39739c:('AString assignment boundary',lambda dest,*_:dest),0x395d22:('AArray add observation boundary',add)})
 return {'return':rc,'added_types':added,'stubs':n.calls}
