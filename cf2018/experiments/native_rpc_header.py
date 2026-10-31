"""Original native binary-header writer with a synthetic memory output sink."""
from native_control import NativeControl, AUX, BUF, STACK


def binary_header(library, *, method='QueryAddrInfo', strict=False,
                  message_type=1, sequence=0x0102030405060708):
    if method not in ('QueryAddrInfo','ReqUpdateVersion','GetUpdateInfo'):
        raise ValueError('independent synthetic allowlisted method required')
    if type(strict) is not bool or message_type not in (1,2,4):
        raise ValueError('bounded synthetic options required')
    if type(sequence) is not int or not 0 <= sequence < 2**64:
        raise ValueError('synthetic unsigned64 required')
    n=NativeControl(library)
    protocol,name=AUX+0x100,AUX+0x200
    n.write(protocol+0x14,AUX+0x300)
    n.write(protocol+0x21,int(strict),1)
    raw=method.encode('ascii')
    n.write(name,BUF+0x100)
    n.write(BUF+0x100-12,len(raw))
    n.uc.mem_write(BUF+0x100,raw)
    n.write(STACK+0xf000,sequence&0xffffffff)
    n.write(STACK+0xf004,sequence>>32)
    chunks=[]
    def write_sink(transport,pointer,count,unused):
        if transport!=AUX+0x300 or count>64 or sum(map(len,chunks))+count>128:
            raise ValueError('synthetic output sink bounds')
        chunks.append(bytes(n.uc.mem_read(pointer,count)))
        return 0
    result=n.execute(0x39c3bc,(protocol,name,message_type,0),{
        0x398ede:('synthetic memory transport sink, no socket',write_sink)})
    return {'return':result,'wire':b''.join(chunks),'write_sizes':[len(c) for c in chunks],
            'stubs':n.calls,'evidence':'NATIVE_HEADER_SYNTHETIC_INPUT_NOT_PHONE_RPC'}
