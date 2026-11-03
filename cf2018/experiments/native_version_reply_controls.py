"""Independent synthetic version fixture and original writer parity.

No actual phone request, route association, endpoint, account or packet send.
All identifiers/version values below are fixed non-sensitive synthetic controls.
"""
from native_control import NativeControl,CTX,BUF,AUX,STOP,STACK
from native_version_callback_controls import METHOD
from native_version_decision_controls import VERSION

def field(kind,ident,data):return bytes([kind])+ident.to_bytes(2,'big')+data
def integer(ident,value=0):return field(8,ident,value.to_bytes(4,'big'))
def long(ident,value=0):return field(10,ident,value.to_bytes(8,'big'))
def string(ident,value=b''):return field(11,ident,len(value).to_bytes(4,'big')+value)

def component(result=0,update_type=0,comm_sequence=7):
    if type(result) is not int or result not in (0,1) or type(update_type) is not int or not 0<=update_type<=3 or type(comm_sequence) is not int or not 0<=comm_sequence<2**31:
        raise ValueError('bounded synthetic component required')
    comm=integer(1,comm_sequence)+integer(2,11)+integer(3,12)+integer(4,20)+long(5,VERSION)+long(6,VERSION)+string(7)+b'\0'
    package=long(1,VERSION)+b''.join(string(i) for i in range(2,7))+b'\0'
    info=field(12,1,package)+integer(2,update_type)+b'\0'
    return field(12,0,integer(1,result)+field(12,2,comm)+field(12,3,info)+b'\0')+b'\0'

def body(sequence=0x100000002,method=METHOD,result=0,update_type=0,comm_sequence=7):
    if type(sequence) is not int or not 0<=sequence<2**64 or type(method) is not str or not 1<=len(method)<=64 or not method.isascii():
        raise ValueError('bounded synthetic RPC header required')
    text=method.encode();return len(text).to_bytes(4,'big')+text+b'\x02'+sequence.to_bytes(8,'big')+component(result,update_type,comm_sequence)

def wire(payload,packet_sequence=0x11223344):
    from directory_config_reply import field as tag
    if type(payload) is not bytes or not 0<len(payload)<=512 or type(packet_sequence) is not int or not 0<=packet_sequence<2**32:
        raise ValueError('bounded synthetic transport fixture required')
    base=b''.join(tag(i,1 if i==6 else 0,v) for i,v in enumerate([0x4366,0,1,0x4013,0,0,packet_sequence,0,len(payload)],1))
    # Deliberately synthetic route: real phone version route is still unknown.
    route=tag(4,5,tag(1,5,b'SyntheticVersion'))
    data=tag(1,1,0)+tag(2,1,0)+tag(3,1,1)+tag(4,5,route)
    header=tag(1,5,base)+tag(2,5,tag(0x4013,5,data))
    return b'\xaa'+(5+len(header)).to_bytes(4,'big')+header+payload

def native_component(library,result=0,update_type=0):
    component(result,update_type) # Validate the same bounded synthetic scalars.
    n=NativeControl(library);proto=AUX+0x100;vtable=AUX+0x200;empty=BUF+0x800
    n.write(proto,vtable);n.write(proto+0x10,64);n.write(empty-12,0);n.write(empty,0,1)
    for offset,value,size in ((4,result,4),(12,7,4),(16,11,4),(20,12,4),(24,20,4),(32,VERSION,8),(40,VERSION,8),(88,VERSION,8),(120,update_type,4),(156,4,1)):
        n.write(BUF+offset,value,size)
    strings=[]
    def capture(slot):
        def event(protocol,where,*unused):
            if protocol!=proto:raise ValueError('synthetic protocol changed')
            if slot==0x54:
                if not BUF<=where<BUF+0xa0:raise ValueError('synthetic string field bound')
                n.write(where,empty);strings.append(where-BUF)
            return 0
        return event
    stubs={}
    for offset in range(0,0x100,4):
        address=STOP+0x400+offset;n.write(vtable+offset,address|1)
        stubs[address]=('synthetic writer/string-fixture discovery',capture(offset))
    n.execute(0x33bef8,(BUF,proto),stubs)
    z=NativeControl(library);z.uc.mem_write(CTX,bytes(n.uc.mem_read(CTX,0x40000)))
    z.write(proto,0x4f4768);z.write(proto+0x14,AUX+0x300)
    pointer=AUX+0x1000;z.write(pointer+4,BUF);z.write(pointer+8,1,1);chunks=[]
    def sink(transport,address,count,*unused):
        if transport!=AUX+0x300 or not 0<=count<=2048:raise ValueError('synthetic writer bound')
        chunks.append(bytes(z.uc.mem_read(address,count)));return 0
    z.execute(0x33deb4,(pointer,proto),{0x398ede:('bounded memory byte sink',sink)})
    return b''.join(chunks),strings

def native_header(library,sequence=0x100000002):
    body(sequence) # Header scalar guard, before binary access.
    n=NativeControl(library);proto=AUX+0x100;name=AUX+0x200
    n.write(proto,0x4f4768);n.write(proto+0x10,64);n.write(proto+0x14,AUX+0x300)
    text=METHOD.encode();n.write(name,BUF);n.write(BUF-12,len(text));n.uc.mem_write(BUF,text)
    n.write(STACK+0xf000,sequence&0xffffffff);n.write(STACK+0xf004,sequence>>32);chunks=[]
    def sink(transport,address,count,*unused):
        if transport!=AUX+0x300 or not 0<=count<=256:raise ValueError('synthetic header sink bound')
        chunks.append(bytes(n.uc.mem_read(address,count)));return 0
    n.execute(0x39c3bc,(proto,name,2,0),{0x398ede:('bounded memory header sink',sink)})
    return b''.join(chunks)
