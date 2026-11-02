"""Exact original NIFS header verifier on a supplied bounded header copy.

Original MD5/validation execute; only libc memcmp is a functional substitute.
No archive/file open, asset content export, networking or original-file write.
"""
from native_control import NativeControl,CTX,BUF,STACK
def verify(library,header):
    if type(header) is not bytes or len(header)!=172:
        raise ValueError('172-byte header copy required')
    n=NativeControl(library);n.write(CTX+0x48,BUF);n.write(STACK+0xf000,0)
    n.uc.mem_write(BUF,header)
    def compare(a,b,count,*unused):
        if count>172:raise ValueError('header comparison bound')
        x=bytes(n.uc.mem_read(a,count));y=bytes(n.uc.mem_read(b,count))
        return (x>y)-(x<y)
    return n.execute(0x293a50,(CTX,0,0,0),{0x193e0c:('bounded functional memcmp',compare)})
