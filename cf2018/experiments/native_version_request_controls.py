"""Original request writer on fixed synthetic values; no connection or send."""
from native_control import NativeControl,AUX,BUF

def route_matches_original(library):
    n=NativeControl(library)
    # Send_ReqUpdateVersion transport setServiceName operand, not a string scan.
    address=(n.read(0x33e524)+0x33e48a)&0xffffffff
    return bytes(n.uc.mem_read(address,14))==b'VersionUpdate\0'

def native_args(library,optional=False):
    if type(optional) is not bool:raise ValueError('boolean optional fields required')
    n=NativeControl(library);req=AUX+0x400;args=AUX+0x500;proto=AUX+0x100;empty=BUF+0x100
    n.write(proto,0x4f4768);n.write(proto+0x10,64);n.write(proto+0x14,AUX+0x300)
    for offset,value,size in ((12,7,4),(16,11,4),(20,1,4),(24,1,4),(32,0x1111222233334444,8),(40,0x1111222233334444,8)):
        n.write(req+offset,value,size)
    n.write(empty-12,0);n.uc.mem_write(empty,b'\0')
    for offset in (0x30,0x48,0x50,0x54,0x58):n.write(req+offset,empty)
    if optional:
        n.write(req+0x42,0x80,1);n.write(req+0x43,1,1);n.write(req+0x60,4,1)
        n.write(req+0x38,23,8);n.write(req+0x40,2,2)
    n.write(args+4,req);chunks=[]
    def sink(transport,pointer,count,*unused):
        if transport!=AUX+0x300 or count>256 or sum(map(len,chunks))+count>2048:raise ValueError('bounded synthetic sink')
        chunks.append(bytes(n.uc.mem_read(pointer,count)));return 0
    n.execute(0x33dc88,(args,proto),{0x398ede:('bounded synthetic request byte sink',sink)})
    return b''.join(chunks)

def fill_profile(library,mode):
    if type(mode) is not int or mode not in (20,21,22,23):raise ValueError('known synthetic updater mode required')
    from native_control import CTX,STOP
    from unicorn.arm_const import UC_ARM_REG_R1
    n=NativeControl(library);cfg=AUX+0x100;vt=AUX+0x200;empty=AUX+0x700;settings=AUX+0x600
    n.write(CTX+0x10,cfg);n.write(cfg,vt);n.write(vt+0x2c,(STOP+0x400)|1)
    n.write(CTX+0x2c,11);n.write(CTX+8,settings);n.write(empty-12,0);n.uc.mem_write(empty,b'\0')
    for where in (CTX+0x24,CTX+0x28,CTX+0x44,CTX+0x48,settings+0x14,BUF+0x30,BUF+0x48,BUF+0x50,BUF+0x54,BUF+0x58):n.write(where,empty)
    def copy(dst,src,*unused):n.write(dst,n.read(src));return dst
    def version(*unused):n.uc.reg_write(UC_ARM_REG_R1,0x11112222);return 0x33334444
    n.execute(0x32e538,(CTX,BUF),{STOP+0x400:('injected config mode getter',mode),0x3f95f4:('bounded synthetic string copy',copy),0x3f96c0:('bounded synthetic string assignment',copy),0x3f8a20:('string destruction boundary',0),0x330318:('synthetic version text conversion boundary',version)})
    return {'product_type':n.read(BUF+0x14),'request_type':n.read(BUF+0x18),'custom_fields':bool(n.read(BUF+0x60,1)&4)}
