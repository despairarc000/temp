"""Bounded original routed-TX controls, stopped before encryption/send."""
from native_control import NativeControl, CTX, BUF, AUX, STACK, STOP


def routed_tx(library, payload, *, state=5, initialized=True, maximum=64,
              timeout=0, route_type=0):
    if type(payload) is not bytes or not 1 <= len(payload) <= 65:
        raise ValueError('independent synthetic payload 1..65 bytes required')
    if state not in (4,5) or type(initialized) is not bool or maximum != 64:
        raise ValueError('bounded context required')
    if timeout not in (-1,0) or route_type not in (0,1):
        raise ValueError('bounded timeout/route required')
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_PC
    n=NativeControl(library)
    n.write(CTX+0x124,int(initialized));n.write(CTX+0x6c8,state)
    n.write(CTX+0x6d0,maximum);n.write(CTX+0x12c,0x01020304)
    n.write(CTX+0x348c,0x77);n.write(CTX+0x2e80,AUX)
    n.uc.mem_write(BUF,payload)
    n.write(STACK+0xf000,route_type);n.write(STACK+0xf004,0);n.write(STACK+0xf008,0)
    capture={}
    def boundary(u,a,size,unused):
        if a==0x3ab430:
            ptr=u.reg_read(UC_ARM_REG_R1);length=u.reg_read(UC_ARM_REG_R2)
            if length>69:raise RuntimeError('unexpected send boundary size')
            prepared=bytes(u.mem_read(ptr,length))
            capture.update(length=length,prefix_matches_big_endian_uid=prepared[:4]==b'\1\2\3\4',
                           payload_preserved=prepared[4:]==payload)
            u.reg_write(UC_ARM_REG_R0,(-77)&0xffffffff);u.reg_write(UC_ARM_REG_PC,STOP|1)
    n.uc.hook_add(UC_HOOK_CODE,boundary)
    code=n.execute(0x3a91ec,(CTX,BUF,len(payload),timeout))
    return {'return':code,'before_encrypt_send':capture,
            'header_type':n.read(CTX+0x2326,2),
            'base_marker':n.read(CTX+0x2320,2),
            'compression_flag':n.read(CTX+0x2340,1),
            'route_type':n.read(CTX+0x2342,1),
            'stubs':n.calls,'evidence':'SYNTHETIC_NATIVE_PRE_ENCRYPT_NOT_PHONE_PAYLOAD'}
