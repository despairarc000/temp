"""Segmented original updater decision/event pipeline on synthetic values.

Original scalar response assignment and event/plugin bridge execute. Runtime
string operations and decision-block exits are explicit boundaries. This is
not complete CreateNextAction, CLR, download, socket or phone execution.
"""
from native_control import NativeControl,CTX,BUF,OUT,AUX,STOP
VERSION=0x1111222233334444

def exercise(library,mode,update_type,status=0,result=0):
    if type(mode) is not int or not 0<=mode<=32 or type(update_type) is not int or not 0<=update_type<=3:
        raise ValueError('bounded synthetic mode/update type required')
    if type(status) is not int or type(result) is not int or status not in (0,1) or result not in (0,1):
        raise ValueError('bounded synthetic callback statuses required')
    from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R7
    def clone(n):
        other=NativeControl(library);other.uc.mem_write(CTX,bytes(n.uc.mem_read(CTX,0x40000)));return other
    def terminal(n,value):
        def stop(*unused):n.uc.reg_write(UC_ARM_REG_LR,STOP|1);return value
        return stop
    n=NativeControl(library);n.write(BUF+4,result);n.write(BUF+0x58,VERSION,8);n.write(BUF+0x78,update_type);n.write(BUF+0x9c,4,1)
    def version_text(dest,*unused):
        pointer=BUF+0x400;n.write(dest,pointer);n.write(pointer-12,1);n.uc.mem_write(pointer,b'S\0');return dest
    def string_copy(dest,source,*unused):
        n.write(dest,n.read(source));return dest
    # No whole ResVersionUpdate assignment substitute: original0x33c214 runs.
    n.execute(0x32d864,(CTX,status,BUF,0),{
        0x3303b4:('synthetic version text conversion',version_text),
        0x3f96c0:('synthetic GNU string pointer assignment',string_copy),
        0x3f95f4:('synthetic GNU string pointer copy',string_copy),
        0x3f8a20:('temporary string destruction boundary',0)})
    response={'completed':bool(n.read(CTX+0x65,1)),'failed':bool(n.read(CTX+0x66,1)),
              'copied_update_type':n.read(CTX+0xe8),'copied_version':n.read(CTX+0xc8,8)}
    if not response['completed']:return {'callback':response,'family':'NOT_ENTERED'}
    dispatch=clone(n);manager=AUX+0x100;factory=AUX+0x200
    dispatch.write(CTX+0x10,manager);dispatch.write(manager,0x4ee8f8)
    dispatch.write(manager+0x6c,factory);dispatch.write(factory+0x60,mode)
    family=dispatch.execute(0x32f35c,(CTX,0,0,0),{
        0x32f3ca:('app-family decision boundary',terminal(dispatch,1)),
        0x32f734:('resource-family decision boundary',terminal(dispatch,2)),
        0x32fa5a:('other-mode exit boundary',terminal(dispatch,3))})
    if family==3:return {'callback':response,'family':'OTHER_MODE'}
    decision=clone(dispatch)
    for register,value in ((UC_ARM_REG_R4,CTX),(UC_ARM_REG_R5,OUT),(UC_ARM_REG_R7,dispatch.uc.reg_read(UC_ARM_REG_R7))):
        decision.uc.reg_write(register,value)
    # Skip intervening string/configuration setup. These original blocks load
    # the version/update type actually copied by ResUpdateCallBack above.
    branch=decision.execute(0x32f46a if family==1 else 0x32f76a,(0,0,0,0),{
        0x32f4e2:('app no-update result boundary',terminal(decision,1)),
        0x32f534:('app update-handling boundary',terminal(decision,2)),
        0x32f7ee:('resource no-update result boundary',terminal(decision,1)),
        0x32f896:('resource update-handling boundary',terminal(decision,2))})
    tag=bytes(decision.uc.mem_read(OUT,24))
    constructor=clone(decision);event=AUX+0x1000;plugin=AUX+0x2000
    constructor.execute(0x3257e8,(event,OUT,0,0))
    bridge=clone(constructor);bridge.write(plugin,0x4ed810)
    bridge.write(plugin+4,123);bridge.write(plugin+8,(STOP+0x800)|1);deliveries=[]
    def capture(handle,info,*unused):
        if handle!=123:raise ValueError('synthetic delegate handle changed')
        deliveries.append(bytes(bridge.uc.mem_read(info,24)));return 0
    bridge.execute(0x2f441c,(event,plugin,0,0),{STOP+0x800:('synthetic managed delegate boundary',capture)})
    if deliveries!=[tag]:raise ValueError('native event/plugin bridge changed tag')
    return {'callback':response,'family':'APP' if family==1 else 'RESOURCE',
            'branch':'NO_UPDATE_RESULT' if branch==1 else 'UPDATE_HANDLING',
            'flags':tuple(tag[:3]),'version_parts':tuple(int.from_bytes(tag[p:p+2],'little') for p in (4,6,8,10)),
            'delegate_calls':len(deliveries)}
