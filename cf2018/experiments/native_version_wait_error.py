"""Exact-build updater failure blocks; explicit synthetic runtime boundaries."""
from native_control import NativeControl,CTX,AUX,OUT,STACK,STOP

def control(library,iteration=1000,update_result=None):
    from unicorn.arm_const import UC_ARM_REG_R4,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R9,UC_ARM_REG_LR
    n=NativeControl(library)
    for register,value in ((UC_ARM_REG_R4,CTX),(UC_ARM_REG_R6,AUX),(UC_ARM_REG_R7,OUT),(UC_ARM_REG_R9,iteration)):
        n.uc.reg_write(register,value)
    n.write(STACK+0xf020,1000)
    def terminal(value):
        def finish(*unused):n.uc.reg_write(UC_ARM_REG_LR,STOP|1);return value
        return finish
    stubs={0x32fede:('failure exit boundary',terminal(17)),0x32fe50:('poll continuation boundary',terminal(34))}
    if update_result is None:
        stubs[0x32fdf6]=('connector Update continuation boundary',terminal(34));entry=0x32fda0
    else:
        stubs[0x3c5248]=('synthetic connector Update status',update_result);entry=0x32fdf6
    result=n.execute(entry,(0,0,0,0),stubs)
    return result,n.read(OUT)

def source_checks(library):
    from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
    n=NativeControl(library);d=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
    def instruction(at):
        i=next(d.disasm(bytes(n.uc.mem_read(at,4)),at));return i.mnemonic,i.op_str
    checks={
      'connected_predicate':instruction(0x32fd3c)==('bl','#0x3c27dc'),
      'threshold_equality_branch':instruction(0x32fda4)==('bne','#0x32fdf6'),
      'iteration_increment':instruction(0x32fed8)==('add.w','sb, sb, #1'),
      'delay_argument_10000':instruction(0x32fed0)==('movw','r0, #0x2710'),
      'reported_error_literal':n.read(0x32ff3c)==154140712,
      'different_update_error_literal':n.read(0x32ff40)==154140708,
    }
    if not all(checks.values()):raise ValueError('updater source predicate changed')
    return checks
