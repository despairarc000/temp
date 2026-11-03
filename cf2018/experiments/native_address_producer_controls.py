"""Original ParseDomainName and whole address RPC writer on synthetic domains.

Actual original instructions and binary-vtable dispatch run locally. Bounded GNU
string/libc substitutes and byte sink; stop before transport flush/setServiceName.
The four-byte packet prefix is modeled separately, never emitted by this sender.
No original bytes, network calls, phone data or reply generation.
"""
from native_control import NativeControl,CTX,BUF,AUX,STOP
def build(library,domain,strict=False):
 if type(domain) is not str or len(domain)>128 or not __import__('re').fullmatch(r'[a-z]{1,16}\.[0-9]{1,8}\.[0-9]{1,12}\.synthetic\.invalid',domain):raise ValueError('synthetic domain required')
 if type(strict) is not bool:raise ValueError('boolean protocol flag required')
 from unicorn.arm_const import UC_ARM_REG_R1,UC_ARM_REG_LR
 n=NativeControl(library);name=AUX+0x100;request=AUX+0x400;heap=[AUX+0x4000]
 def cstring(pointer):return bytes(n.uc.mem_read(pointer,256)).split(b'\0',1)[0]
 def get(owner):
  pointer=n.read(owner);count=n.read(pointer-12)
  if count>255:raise ValueError('string bound')
  return bytes(n.uc.mem_read(pointer,count))
 def put(owner,data):
  if len(data)>255:raise ValueError('string bound')
  pointer=heap[0]+12;heap[0]+=(len(data)+32+15)&~15
  n.write(owner,pointer);n.write(pointer-12,len(data));n.write(pointer-8,len(data));n.write(pointer-4,0);n.uc.mem_write(pointer,data+b'\0');return owner
 def copy(dst,src,*unused):return put(dst,get(src))
 def find(owner,needle,start,*unused):
  value=get(owner).find(cstring(needle),start);return value if value>=0 else 0xffffffff
 def substr(dst,owner,start,count):return put(dst,get(owner)[start:] if count==0xffffffff else get(owner)[start:start+count])
 def atoi(pointer,*unused):return int(cstring(pointer))
 def atoll(pointer,*unused):
  value=int(cstring(pointer));n.uc.reg_write(UC_ARM_REG_R1,(value>>32)&0xffffffff);return value&0xffffffff
 put(name,domain.encode())
 rc=n.execute(0x3993c8,(name,request),{0x3f95f4:('bounded GNU string copy',copy),0x3f96c0:('bounded GNU string assignment',copy),0x3f848c:('bounded GNU string find',find),0x3f9834:('bounded GNU substring',substr),0x3f8a20:('string destruction boundary',0),0x193dd0:('bounded synthetic atoi',atoi),0x194658:('bounded synthetic atoll',atoll)})
 service=get(request+24);game=n.read(request+8,8);unit=n.read(request+16,8)
 z=NativeControl(library);z.uc.mem_write(CTX,bytes(n.uc.mem_read(CTX,0x40000)));p=AUX+0x200;z.write(CTX+0x28,p);z.write(CTX+0x30,1,8);z.write(p,0x4f4768);z.write(p+0x10,64);z.write(p+0x14,AUX+0x300);z.write(p+0x21,int(strict),1);chunks=[];header_names=[];zheap=[AUX+0x8000]
 def construct(dst,src,*unused):
  data=bytes(z.uc.mem_read(src,128)).split(b'\0',1)[0];header_names.append(data)
  pointer=zheap[0]+12;zheap[0]+=(len(data)+32+15)&~15;z.write(dst,pointer);z.write(pointer-12,len(data));z.uc.mem_write(pointer,data+b'\0');return dst
 def sink(t,pointer,count,*unused):
  if t!=AUX+0x300 or count>256 or sum(map(len,chunks))+count>512:raise ValueError('sink bound')
  chunks.append(bytes(z.uc.mem_read(pointer,count)));return 0
 def stop(*unused):z.uc.reg_write(UC_ARM_REG_LR,STOP|1);return 0
 z.execute(0x3998d4,(CTX,request),{0x3f9b6c:('bounded static method-name string',construct),0x3f8a20:('string destruction boundary',0),0x398ede:('bounded protocol byte sink',sink),0x399928:('stop before transport flush/callback',stop)})
 return {'parse_return':rc,'service':service,'game':game,'unit':unit,'body':bytes(4)+b''.join(chunks),'method':header_names}
