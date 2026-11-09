"""Read-only original package integrity audit; no game writes or original-data export."""
import hashlib,struct,time
from zipfile import ZipFile
from native_integrity_controls import prepare_tprt_text_for_audit,STACK,STOP,CTX


def cstring(u,address,limit=4096):
    out=bytearray()
    while len(out)<limit:
        count=min(32,4096-(address%4096),limit-len(out));block=bytes(u.mem_read(address,count))
        if b'\0'in block:return bytes(out)+block.split(b'\0',1)[0]
        out+=block;address+=count
    raise ValueError('bounded C string required')

def run_native(n,entry,args):
    from elftools.elf.elffile import ELFFile
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP
    with open(n.audit_library_path,'rb') as f:
        e=ELFFile(f);rs=e.get_section_by_name('.rel.plt');sym=e.get_section(rs['sh_link']);plt=e.get_section_by_name('.plt')
        pb=plt['sh_addr'];pe=pb+plt['sh_size']
        imports={pb+20+12*i:sym.get_symbol(r['r_info_sym']).name for i,r in enumerate(rs.iter_relocations())}
    if not hasattr(n,'audit_heap'):
        n.u.mem_map(0x3000000,0x400000);n.audit_heap=0x3000000
    done=[];events=set()
    def hook(u,pc,size,unused):
        if pc==STOP:done.append(True);u.emu_stop();return
        if pc not in imports:raise RuntimeError('unmodeled import resolver')
        name=imports[pc];args=[u.reg_read(r)for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];events.add(name)
        if name in ['memcpy','memmove']:
            assert args[2]<=0x20000;u.mem_write(args[0],bytes(u.mem_read(args[1],args[2])));result=args[0]
        elif name=='memset':
            assert args[2]<=0x20000;u.mem_write(args[0],bytes([args[1]&255])*args[2]);result=args[0]
        elif name=='memcmp':
            assert args[2]<=0x20000
            left=bytes(u.mem_read(args[0],args[2]));right=bytes(u.mem_read(args[1],args[2]))
            result=next((x-y for x,y in zip(left,right) if x!=y),0)&0xffffffff
        elif name=='malloc':
            assert 0<args[0]<=0x100000
            result=n.audit_heap;n.audit_heap+=(args[0]+15)&~15
            assert n.audit_heap<0x3400000
        elif name=='free':
            assert args[0]==0 or 0x3000000<=args[0]<n.audit_heap
            result=0
        elif name=='strlen':
            result=len(cstring(u,args[0]))
        elif name=='strcmp':
            left=cstring(u,args[0]);right=cstring(u,args[1])
            result=((left>right)-(left<right))&0xffffffff
        elif name=='snprintf':
            fmt=bytes(u.mem_read(args[2],32)).split(b'\0')[0];assert fmt==b'%08x'
            value=u.reg_read(UC_ARM_REG_R3);output=('%08x'%value).encode();assert 1<=args[1]<=64
            u.mem_write(args[0],output[:args[1]-1]+b'\0');result=len(output)
        elif name in ['__aeabi_atexit','__cxa_atexit']:
            result=0
        else:raise RuntimeError('unmodeled import '+name)
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],list(args)+[0]*4):n.u.reg_write(reg,value)
    n.u.reg_write(UC_ARM_REG_SP,STACK+0xf000);n.u.reg_write(UC_ARM_REG_LR,STOP|1)
    handles=[n.u.hook_add(UC_HOOK_CODE,hook,begin=pb,end=pe-1),n.u.hook_add(UC_HOOK_CODE,hook,begin=STOP,end=STOP+2)]
    started=time.monotonic()
    try:n.u.emu_start(entry|1,STOP+2,timeout=5000000,count=20000000)
    finally:
        for handle in handles:n.u.hook_del(handle)
    if not done:raise RuntimeError('bounded native operation did not finish')
    result=n.u.reg_read(UC_ARM_REG_R0)
    summary={'native_return':result,'seconds':round(time.monotonic()-started,3),'modeled_imports':sorted(events),'raw_output_written':False}
    return result,summary

def initialize_archive_configuration(n,source):
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R4
    with ZipFile(source)as z:infos=z.infolist()
    stack=STACK+0xf000;record=0x1006000;path=0x1006100
    n.u.mem_write(path,b'/synthetic/owned.apk\0');n.write(stack+0x14,path)
    n.u.reg_write(UC_ARM_REG_R4,record)
    def io(u,pc,size,unused):
        if pc==0x61ec:
            u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,STOP|1);return
        if pc==0xc54a:result=1
        else:
            index=u.reg_read(UC_ARM_REG_R1)
            if index>=len(infos):result=0xffffffff
            else:
                entry=infos[index];out=u.reg_read(UC_ARM_REG_R2);meta=u.reg_read(UC_ARM_REG_R3)
                name=entry.filename.encode();assert len(name)<1024
                u.mem_write(out,struct.pack('<I',len(name))+name+b'\0')
                data=bytearray(80);struct.pack_into('<I',data,0x14,entry.CRC);u.mem_write(meta,bytes(data));result=0
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    hs=[n.u.hook_add(UC_HOOK_CODE,io,begin=a,end=a)for a in [0xc54a,0xc564,0x61ec]]
    try:run_native(n,0x614a,[])
    finally:
        for h in hs:n.u.hook_del(h)
    archive_facts=bytes(n.u.mem_read(record,24))
    def facts(u,pc,size,unused):
        target=u.reg_read(UC_ARM_REG_R0);u.mem_write(target,archive_facts)
        u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    h=n.u.hook_add(UC_HOOK_CODE,facts,begin=0x60b8,end=0x60b8)
    try:run_native(n,0x62fc,[])
    finally:n.u.hook_del(h)
    return {'archive_libraries_seen':sum(x==1 for x in archive_facts[:4]),'archive_io_modeled':True}

def prepared_metadata(library,original_apk):
    from pathlib import Path
    if hashlib.sha256(Path(original_apk).read_bytes()).hexdigest()!='33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9':
        raise ValueError('exact original APK required')
    n,info=prepare_tprt_text_for_audit(library)
    n.audit_library_path=str(library)
    for entry in [0x27b8,0x2960]:run_native(n,entry,[])
    initialize_archive_configuration(n,original_apk)
    with ZipFile(original_apk)as z:raw=z.read('assets/__tpinfo.tsa')
    address=0x2000000;n.u.mem_map(address,0x20000);n.u.mem_write(address,raw)
    result,summary=run_native(n,0x41f8,[address,len(raw),1])
    return n,address,len(raw),summary

def parse_records(n,base,length):
    if not 0<length<=0x20000:raise ValueError('bounded metadata payload required')
    records=[];offset=0
    while offset<length and len(records)<4096:
        raw=bytes(n.u.mem_read(base+offset,min(4096,length-offset)))
        if len(raw)<13:raise ValueError('short metadata record')
        size=struct.unpack_from('<H',raw)[0]
        if not 13<=size<=len(raw):raise ValueError('metadata record extent')
        name=raw[12:size].split(b'\0',1)[0].decode('utf8')
        if not name or name.startswith('/') or '..'in name.split('/'):raise ValueError('metadata member path')
        crc,length_value=struct.unpack_from('<II',raw,4)
        records.append((name,crc,length_value));offset+=size
    if offset!=length or len({r[0]for r in records})!=len(records):raise ValueError('metadata count/uniqueness')
    return records

def signature(name,crc,size):
    import zlib
    return zlib.crc32(name.encode('utf8')+struct.pack('<II',size,crc))

def signature_set(entries):return {signature(*entry)for entry in entries}

def native_count_guard(n,matched,expected):
    n.write(STACK+0xf000+0x10,matched);n.write(STACK+0xf000+0x20,expected)
    result=[]
    def boundary(u,address):
        if address in (0x17dfa,0x17dd4):result.append(address==0x17dfa);return True
        return False
    n.execute(0x17df2,(),boundary)
    if len(result)!=1:raise ValueError('native count boundary missing')
    return result[0]

def archive_entries(path):
    import zlib
    with ZipFile(path)as z:
        infos=z.infolist()
        if len(infos)>4096 or len({i.filename for i in infos})!=len(infos):raise ValueError('archive entry budget/uniqueness')
        if sum(i.file_size for i in infos)>256*1024*1024 or any(i.file_size>32*1024*1024 for i in infos):raise ValueError('archive payload budget')
        for entry in infos:
            if zlib.crc32(z.read(entry))!=entry.CRC:raise ValueError('archive payload CRC mismatch')
        return [(i.filename,i.CRC,i.file_size)for i in infos]

def audit(library,original_apk,comparisons):
    if any(role not in ['signature_control','scoped_trust']for role in comparisons):raise ValueError('fixed comparison labels required')
    n,address,size,transform=prepared_metadata(library,original_apk)
    with ZipFile(original_apk)as z:
        header=z.read('assets/__tpcfinfo.tsa');expected_crc=z.getinfo('assets/__tpinfo.tsa').CRC
        original_metadata=z.read('assets/__tpinfo.tsa')
    # Verify changes against the original integrity verifier, not a guessed encoder.
    verify_address=0x2080000;n.u.mem_map(verify_address,0x20000)
    verification={}
    for label,changed_at in [('original_accepted',None),('payload_change_rejected',40),
                             ('verification_block_change_rejected',len(original_metadata)-64)]:
        candidate=bytearray(original_metadata)
        if changed_at is not None:candidate[changed_at]^=1
        n.u.mem_write(verify_address,bytes(candidate))
        value,_=run_native(n,0x41f8,[verify_address,len(candidate),1])
        verification[label]=(value==1 if changed_at is None else value==0)
    if not all(verification.values()):raise ValueError('metadata verification negative control failed')
    header_address=CTX+0x7000;header_out=CTX+0x7200;n.u.mem_write(header_address,header)
    accepted,_=run_native(n,0x5250,[header_out,header_address,len(header)])
    if accepted!=1 or n.read(header_out)!=expected_crc:raise ValueError('original metadata/header binding rejected')
    obj=CTX+0x5000;n.u.mem_write(obj,bytes(32))
    accepted,_=run_native(n,0x54c0,[obj,address,size])
    if accepted!=1:raise ValueError('native metadata container rejected')
    iterator,_=run_native(n,0x5550,[obj])
    records=parse_records(n,n.read(iterator),n.read(iterator+4))
    # Independent native record-reader check before trusting host layout.
    for expected in records[:4]:
        if not run_native(n,0x54e0,[iterator])[0]:raise ValueError('native record count disagreement')
        pointer,_=run_native(n,0x5500,[iterator])
        actual=(cstring(n.u,pointer+12).decode(),n.read(pointer+4),n.read(pointer+8))
        if actual!=expected:raise ValueError('native record layout disagreement')
    original=archive_entries(original_apk);lookup={name:(crc,length)for name,crc,length in original}
    if any(lookup.get(name)!=(crc,length)for name,crc,length in records):raise ValueError('original metadata records do not match source')
    samples=[records[0]]+[r for r in records if r[0]in ['AndroidManifest.xml','resources.arsc','classes.dex']]
    for name,crc,length in samples:
        n.u.mem_write(CTX+0x7400,name.encode()+b'\0')
        native,_=run_native(n,0x43d4,[CTX+0x7400,length,crc])
        if native!=signature(name,crc,length):raise ValueError('native signature composition disagreement')
    expected=signature_set(records)
    if len(expected)!=len(records):raise ValueError('original metadata signature collision')
    results={}
    for role,path in [('original',original_apk)]+list(comparisons.items()):
        actual=signature_set(original if role=='original'else archive_entries(path));matched=len(expected&actual)
        results[role]={'matched_protected_records':matched,
                       'mismatched_members':[name for name,crc,length in records if signature(name,crc,length)not in actual],
                       'native_count_gate_passed':native_count_guard(n,matched,len(records))}
    extra=signature_set(original+[('res/xml/synthetic_extra.xml',123,456)])
    changed=[(name,crc^1,length)if name=='AndroidManifest.xml'else(name,crc,length)for name,crc,length in original]
    negatives={'unlisted_extra_preserves_count':native_count_guard(n,len(expected&extra),len(records)),
               'single_changed_manifest_rejected':not native_count_guard(n,len(expected&signature_set(changed)),len(records))}
    return {'format':'CF2018_OFFLINE_PACKAGE_INTEGRITY_AUDIT','protected_record_count':len(records),
            'native_header_binding_verified':True,'native_record_layout_verified':True,
            'native_signature_composition_verified':True,'archive_payload_crcs_verified':True,
            'comparisons':results,'synthetic_negative_controls':negatives,
            'native_metadata_verification_controls':verification,
            'phone_call_stack_observed':False,'android_initialization_performed':False,
            'game_files_modified':False,'keys_or_original_data_exported':False,
            'limits':'Native checks with explicit memory/archive service models; not full phone execution.'}

if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library',type=Path,required=True);p.add_argument('--original',type=Path,required=True)
    p.add_argument('--signature-control',type=Path);p.add_argument('--scoped-trust',type=Path)
    args=p.parse_args();comparisons={}
    if args.signature_control:comparisons['signature_control']=args.signature_control
    if args.scoped_trust:comparisons['scoped_trust']=args.scoped_trust
    try:print(json.dumps(audit(args.library,args.original,comparisons),indent=2))
    except Exception:raise SystemExit('Audit did not complete; no original data or raw exception exported.')


