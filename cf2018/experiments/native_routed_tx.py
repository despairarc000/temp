"""Bounded original routed-TX controls; every actual socket send is suppressed."""
from native_control import NativeControl, CTX, BUF, AUX, STACK, STOP


def routed_tx(library, payload, *, state=5, initialized=True, maximum=64,
              timeout=0, route_type=0, finish_native=False):
    if type(payload) is not bytes or not 1 <= len(payload) <= 65:
        raise ValueError('independent synthetic payload 1..65 bytes required')
    if state not in (4,5) or type(initialized) is not bool or maximum != 64:
        raise ValueError('bounded context required')
    if timeout not in (-1,0) or route_type not in (0,1):
        raise ValueError('bounded timeout/route required')
    if type(finish_native) is not bool:
        raise ValueError('boolean finish control required')
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_PC
    n=NativeControl(library)
    n.write(CTX+0x124,int(initialized));n.write(CTX+0x6c8,state)
    n.write(CTX+0x6d0,maximum);n.write(CTX+0x12c,0x01020304)
    n.write(CTX+0x348c,0x77);n.write(CTX+0x2e80,AUX)
    n.write(CTX+0x2308,AUX+0x1000);n.write(CTX+0x230c,4096)
    n.uc.mem_write(BUF,payload)
    n.write(STACK+0xf000,route_type);n.write(STACK+0xf004,0);n.write(STACK+0xf008,0)
    capture={}
    def boundary(u,a,size,unused):
        if a==0x3ab430:
            ptr=u.reg_read(UC_ARM_REG_R1);length=u.reg_read(UC_ARM_REG_R2)
            if length>69:raise RuntimeError('unexpected send boundary size')
            prepared=bytes(u.mem_read(ptr,length))
            capture.update(length=length,prefix_matches_big_endian_sequence=prepared[:4]==b'\1\2\3\4',
                           payload_preserved=prepared[4:]==payload)
            if not finish_native:
                u.reg_write(UC_ARM_REG_R0,(-77)&0xffffffff);u.reg_write(UC_ARM_REG_PC,STOP|1)
    n.uc.hook_add(UC_HOOK_CODE,boundary)
    stubs={0x3ab3a6:('send-buffer submission SUPPRESSED; no socket',-77)} if finish_native else {}
    code=n.execute(0x3a91ec,(CTX,BUF,len(payload),timeout),stubs)
    queued_length=n.read(CTX+0x2314)
    if queued_length>4096:raise RuntimeError('queued synthetic wire exceeds capacity')
    queued=bytes(n.uc.mem_read(AUX+0x1000,queued_length))
    return {'return':code,'before_encrypt_send':capture,
            'header_type':n.read(CTX+0x2326,2),
            'base_marker':n.read(CTX+0x2320,2),
            'compression_flag':n.read(CTX+0x2340,1),
            'route_type':n.read(CTX+0x2342,1),
            'sequence_incremented':n.read(CTX+0x12c)==0x01020305,
            'pending_wire_length':queued_length,
            'queued_body_preserved':bool(queued) and queued.endswith(b'\1\2\3\4'+payload),
            'stubs':n.calls,'evidence':'SYNTHETIC_NATIVE_PRE_ENCRYPT_NOT_PHONE_PAYLOAD'}


def encrypt_boundary(library, *, method=0, compression=0, capacity=8):
    """Original native helper; mode0 copy or encrypted-method missing-key failure.

    No keys, socket, ciphertext or phone input; compression field is independent.
    """
    if method not in (0,3,4) or compression not in (0,1) or capacity not in (0,4,8):
        raise ValueError('bounded crypto/compression controls required')
    from native_control import OUT
    n=NativeControl(library)
    payload=b'LABDATA!'
    n.uc.mem_write(BUF,payload);n.uc.mem_write(AUX,b'R'*8)
    n.write(CTX+0x11c,method)
    n.write(CTX+0x33f4,compression)
    n.write(CTX+0x458,0,1)
    n.write(OUT,capacity);n.write(STACK+0xf000,OUT)
    code=n.execute(0x3ab296,(CTX,BUF,len(payload),AUX))
    return {'return':code,'output_length':n.read(OUT),
            'payload_copied':bytes(n.uc.mem_read(AUX,8))==payload,
            'output_unchanged':bytes(n.uc.mem_read(AUX,8))==b'R'*8,
            'stubs':n.calls,'evidence':'SYNTHETIC_NATIVE_NO_KEY_NOT_V38_CRYPTO_OBSERVATION'}
