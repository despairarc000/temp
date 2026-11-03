"""Original version callback with synthetic inputs and explicit copy boundaries.

No network, packet decoder, full RPC dispatch, Android or asset acceptance.
"""
from native_control import NativeControl,CTX,BUF,AUX,STOP
METHOD='VersionUpdate:ReqUpdateVersion'

def method_name(library):
    n=NativeControl(library)
    # Generated send method's PC-relative string construction, not a scan hit.
    address=(n.read(0x33e51c)+0x33e41a)&0xffffffff
    name=bytes(n.uc.mem_read(address,128)).split(b'\0',1)[0].decode('ascii')
    if name!=METHOD:raise ValueError('generated updater method changed')
    return name

def callback(library,status,result):
    if type(status) is not int or type(result) is not int or not 0<=status<2**32 or not 0<=result<2**32:
        raise ValueError('synthetic u32 statuses required')
    n=NativeControl(library);n.write(BUF+4,result);copies=[]
    def version_text(dest,unused,low,high):
        pointer=BUF+0x400;n.write(dest,pointer);n.write(pointer-12,1)
        n.uc.mem_write(pointer,b'S\0');return dest
    def copy_response(dest,source,*unused):
        if dest!=CTX+0x70 or source!=BUF:raise ValueError('unexpected copy boundary')
        copies.append('response');return dest
    def copy_version(dest,source,*unused):
        if dest!=CTX+0x68:raise ValueError('unexpected version string boundary')
        copies.append('version');return dest
    n.execute(0x32d864,(CTX,status,BUF,0),{
        0x3303b4:('synthetic version-number text conversion',version_text),
        0x33c214:('response assignment boundary',copy_response),
        0x3f96c0:('version string assignment boundary',copy_version),
        0x3f8a20:('temporary string destruction boundary',0)})
    return {'completed':bool(n.read(CTX+0x65,1)),
            'failed':bool(n.read(CTX+0x66,1)),'copy_boundaries':copies}

def writer_schema(library,optional=False):
    """Original generated writer; synthetic protocol records schema only."""
    import re
    if type(optional) is not bool:raise ValueError('synthetic presence flag required')
    n=NativeControl(library);proto=AUX+0x100;vtable=AUX+0x200;events=[]
    n.write(proto,vtable);n.write(proto+0x10,64)
    n.write(BUF+0x9c,0xff if optional else 0,1)
    def event(slot):
        def call(protocol,name,kind,ident):
            if protocol!=proto:raise ValueError('protocol boundary changed')
            if slot in (0x10,0x18):
                value=bytes(n.uc.mem_read(name,128)).split(b'\0',1)[0]
                if not re.fullmatch(rb'[A-Za-z_][A-Za-z0-9_]{0,60}',value):raise ValueError('schema label bound')
                events.append(('struct',value.decode()) if slot==0x10 else ('field',value.decode(),kind,ident))
            return 0
        return call
    stubs={}
    for offset in range(0,0x100,4):
        address=STOP+0x400+offset;n.write(vtable+offset,address|1)
        stubs[address]=('synthetic protocol schema event',event(offset))
    n.execute(0x33bef8,(BUF,proto,0,0),stubs)
    return events

def read_component(library,wire):
    """Original pointer-result reader, bounded synthetic input; no reply send."""
    if type(wire) is not bytes or not 0<len(wire)<=2048:raise ValueError('bounded synthetic component required')
    n=NativeControl(library);proto=AUX+0x100;target=AUX+0x1000;result=AUX+0x2000
    n.write(proto,0x4f4768);n.write(proto+0x10,64);n.write(proto+0x14,AUX+0x300);n.write(result+4,target)
    cursor=[0];heap=[AUX+0x4000]
    def allocate(size,*unused):
        if not 0<size<=4096 or heap[0]+size>=CTX+0x40000:raise ValueError('synthetic allocation bound')
        address=heap[0];heap[0]+=(size+15)&~15;return address
    def string(protocol,dest,count,*unused):
        if not 0<=count<=1024:raise ValueError('synthetic string bound')
        pointer=allocate(count+16)+12
        if count:read(AUX+0x300,pointer,count)
        n.write(dest,pointer);n.write(pointer-12,count);n.write(pointer-8,count);n.write(pointer-4,0);n.write(pointer+count,0,1)
        return count
    def strlen(pointer,*unused):return len(bytes(n.uc.mem_read(pointer,1024)).split(b'\0',1)[0])
    def read(transport,dest,count,*unused):
        if transport!=AUX+0x300 or not 0<=count<=1024 or cursor[0]+count>len(wire):raise ValueError('synthetic input truncation/bound')
        if count:n.uc.mem_write(dest,wire[cursor[0]:cursor[0]+count])
        cursor[0]+=count;return count
    n.execute(0x33ddfc,(result,proto,0,0),{
        0x3c93fc:('bounded synthetic allocation',allocate),
        0x3c9bec:('free boundary',0),
        0x193e00:('bounded strlen',strlen),
        0x39c6a4:('bounded GNU string storage',string),
        0x398df4:('bounded synthetic memory reader',read),
        0x398182:('bounded synthetic memory reader',read),
        0x3f8a20:('temporary string destruction boundary',0)})
    return {'consumed':cursor[0],'success_present':bool(n.read(result+8,1)&1),
            'result':n.read(target+4),'presence_flags':n.read(target+0x9c,1)}
