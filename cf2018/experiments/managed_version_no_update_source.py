"""Hash-pinned managed no-update predicates; metadata/calls only, no CLR."""
from struct import unpack_from
from managed_directory_config_metadata import KNOWN_SHA

def check(m,decode_calls):
    if m.sha!=KNOWN_SHA:raise ValueError('exact original managed source required')
    b=m.b;u16=lambda p:unpack_from('<H',b,p)[0];u32=lambda p:unpack_from('<I',b,p)[0]
    root=0x5fbf1c;p=(root+16+u32(root+12)+3)&~3;count=u16(p+2);p+=4;blob=None
    for _ in range(count):
        offset,length=u32(p),u32(p+4);end=b.index(0,p+8,p+128)
        if b[p+8:end]==b'#Blob':blob=root+offset
        p=(end+4)&~3
    if blob is None:raise ValueError('source blob heap missing')
    fields={}
    for rid in (0xba91,0xba92,0xba93):
        row=m.starts[4]+(rid-1)*m.sizes[4];offset=u32(row+6)
        fields[rid]=(m.str_at(u32(row+2)),b[blob+offset:blob+offset+3])
    # Find the original ClientState.Succeeded Constant row, not ordinal guessing.
    ti=0x1414-1
    if m.typedef[ti][0]!='ClientState':raise ValueError('state enum identity changed')
    first=u32(m.starts[2]+ti*m.sizes[2]+14);last=u32(m.starts[2]+(ti+1)*m.sizes[2]+14)
    matched=[r for r in range(first,last) if m.str_at(u32(m.starts[4]+(r-1)*m.sizes[4]+2))=='Succeeded']
    if len(matched)!=1:raise ValueError('source state field changed')
    width=2 if max(m.rows.get(t,0) for t in (4,8,23))<16384 else 4
    base=m.starts[10]+m.rows[10]*m.sizes[10];values=[]
    for j in range(m.rows[11]):
        row=base+j*(2+width+4);parent=int.from_bytes(b[row+2:row+2+width],'little')
        if parent!=matched[0]<<2:continue
        off=u32(row+2+width)
        if b[row]!=8 or b[blob+off]!=4:raise ValueError('state constant shape changed')
        values.append(u32(blob+off+1))
    def body(rid):return m.body(m.methods[rid-1][0])
    def field(rid,pc,token):
        code=body(rid);return code[pc]==0x7b and int.from_bytes(code[pc+1:pc+5],'little')==token
    def branch(rid,pc,opcode,target):
        code=body(rid);return code[pc]==opcode and pc+5+int.from_bytes(code[pc+1:pc+5],'little',signed=True)==target
    def success_call(rid,pc):
        code=body(rid);calls=decode_calls(code)
        return code[pc-2:pc]==bytes((2,0x1d)) and any(p==pc and token==0x0600a909 for p,op,token in calls or [])
    checks={
      'versioninfo_three_u8_fields':fields=={0xba91:('isAppUpdating',bytes((2,6,5))),0xba92:('isNeedUpdating',bytes((2,6,5))),0xba93:('isForcedUpdating',bytes((2,6,5)))},
      'succeeded_state_is_seven':values==[7],
      'apk_checks_need_update':field(0xa94e,0x3b,0x0400ba92) and branch(0xa94e,0x40,0x3a,0x51),
      'apk_also_checks_forced_update':field(0xa94e,0x47,0x0400ba93) and branch(0xa94e,0x4c,0x39,0x147),
      'apk_no_update_reaches_succeeded':success_call(0xa94e,0x159),
      'resource_checks_need_update':field(0xa92c,0xd8,0x0400ba92) and branch(0xa92c,0xdd,0x39,0x2d7),
      'resource_no_update_reaches_succeeded':success_call(0xa92c,0x2e9),
    }
    if not all(checks.values()):raise ValueError('managed no-update predicates changed: '+','.join(k for k,v in checks.items() if not v))
    return checks
