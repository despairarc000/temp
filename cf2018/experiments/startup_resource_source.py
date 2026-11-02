"""Build-pinned read-only startup/resource call checks; no CLR, sockets or game.

Managed metadata is supplied by the existing private original inspector. Native
checks only decode specified direct-call instructions from hash-verified Apollo.
Symbols/check names are exported; original bodies and values are never saved.
"""
from managed_directory_config_metadata import KNOWN_SHA

def managed_checks(metadata,decode_calls):
 if metadata.sha!=KNOWN_SHA:raise ValueError('exact original DLL required')
 def body(token):return metadata.body(metadata.methods[(token&0xffffff)-1][0])
 def calls(token):
  code=body(token);result=decode_calls(code)
  if result is None:raise ValueError('CIL instruction walk failed')
  return {(pc,target) for pc,_,target in result}
 def has(token,pc,target):return (pc,target) in calls(token)
 def float_return(token,value):
  import struct
  code=body(token)
  return len(code)==6 and code[0]==0x22 and code[-1]==0x2a and struct.unpack_from('<f',code,1)[0]==value
 checks={
  'directory_timeout_30_seconds':float_return(0x0600a7eb,30),
  'base_start_reads_virtual_runtime_limit':has(0x06005df0,0x18,0x06005dec),
  'base_start_binds_virtual_overtime':has(0x06005df0,0x2e,0x06005df6),
  'version_flow_zero_runtime_limit':float_return(0x0600a86b,0),
  'directory_overtime_can_finish':has(0x0600a7ef,0x3f,0x0600a7ed),
  'directory_finish_reaches_base_finish':has(0x0600a7ed,0x20,0x06005df4),
  'normal_directory_callback_has_independent_finish':has(0x0600a7f1,0xa3,0x06005df4),
  'version_flow_enters_update_controller':has(0x0600a868,0x53,0x0600a95f),
  'controller_reads_bundled_tversion':has(0x0600a95f,0x64,0x060001ed),
  'controller_starts_version_check':has(0x0600a95f,0x6f,0x0600a960),
  'controller_sets_server_config':has(0x0600a960,0x2f,0x0600a961),
  'controller_extract_candidate':has(0x0600a960,0x3f,0x0600a965),
  'controller_apk_candidate':has(0x0600a960,0x4a,0x0600a963),
  'resource_check_starts_iips':has(0x0600a968,0x30,0x0600a911),
  'iips_tick_drives_check':has(0x0600a912,0x79,0x0600a90b),
  'iips_check_starts_version_query':has(0x0600a90b,0x7,0x0600a90d),
  'extract_decision_compares_persisted_version':has(0x0600a93f,0x3e,0x0600a90e),
  'extract_can_succeed_locally':has(0x0600a942,0x5f,0x0600a947),
  'apk_tick_can_continue_to_extract':has(0x0600a964,0x50,0x0600a965),
  'extract_tick_can_continue_to_resource':has(0x0600a966,0x8a,0x0600a968),
 }
 # External interface symbols are checked without treating their managed bodies
 # as locally defined or executed.
 external={pc:metadata.fq(target) for pc,_,target in decode_calls(body(0x0600a90d))}
 checks['native_version_manager_created']=external.get(0xac)=='IIPSMobile.IIPSMobileVersion.CreateVersionMgr'
 checks['native_app_update_requested']=external.get(0xc7)=='IIPSMobile.IIPSMobileVersionMgrInterface.MgrCheckAppUpdate'
 base_start={pc:metadata.fq(target) for pc,_,target in decode_calls(body(0x06005df0))}
 checks['base_start_registers_timer']=base_start.get(0x3a)=='WNGUI.UIWindowController.StartTimer'
 if not all(checks.values()):raise ValueError('source checks failed: '+','.join(k for k,v in checks.items() if not v))
 return checks

NATIVE_EDGES=((0x32fbe2,0x3c31a0), # RpcConnector constructor
              (0x32fc74,0x3c4530), # RpcConnector::Init
              (0x32fd9a,0x32e6d4), # gcloud updater doGetVersion
              (0x32fdf8,0x3c5248), # RpcConnector::Update
              (0x32e6f8,0x33effc), # VersionUpdateClient constructor
              (0x32e7ac,0x32e538)) # FillReqUpdate

def native_checks(library):
 from native_control import NativeControl
 from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
 n=NativeControl(library);decoder=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
 checked=[]
 for site,target in NATIVE_EDGES:
  ins=next(decoder.disasm(bytes(n.uc.mem_read(site,4)),site),None)
  if ins is None or ins.mnemonic!='bl' or ins.op_str!=f'#{target:#x}':
   raise ValueError('native source call mismatch at '+hex(site))
  checked.append((site,target))
 return checked
