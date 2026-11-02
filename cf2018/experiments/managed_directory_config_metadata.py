"""Read-only build-specific metadata checks using the existing private inspector.

Accepts an already hash-verified Metadata object; exports symbols/checks only.
No original method body, decoded image or account data is written.
"""
from struct import unpack_from
KNOWN_SHA='174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9'
def check(m,decode_calls):
 if m.sha!=KNOWN_SHA or m.heap_flags!=5:raise ValueError('exact original metadata required')
 b=m.b
 u16=lambda p:unpack_from('<H',b,p)[0]
 u32=lambda p:unpack_from('<I',b,p)[0]
 idx=lambda t:2 if m.rows.get(t,0)<65536 else 4
 coded=lambda bits,ts:2 if max(m.rows.get(t,0) for t in ts)<1<<(16-bits) else 4
 sizes={11:2+coded(2,(4,8,23))+4,12:coded(5,(6,4,1,2,8,9,10,0,14,23,20,17,26,27,32,35,38,39,40,42,44,43))+coded(3,(6,10))+4,13:coded(1,(4,8))+4,14:2+coded(2,(2,6,32))+4,15:6+idx(2),16:4+idx(4),17:4,18:idx(2)+idx(20),19:idx(20),20:6+coded(2,(2,1,27)),21:idx(2)+idx(23),22:idx(23),23:10,24:2+idx(6)+coded(1,(20,23)),25:idx(2)+2*coded(1,(6,10)),26:4,27:4,28:2+coded(1,(4,6))+4+idx(26),29:4+idx(4),30:8,31:4,32:28,33:4,34:12,35:28,36:4+idx(35),37:12+idx(35),38:12,39:16+coded(2,(38,35,39)),40:12+coded(2,(38,35,39)),41:2*idx(2),42:4+coded(1,(2,6))+4,43:coded(1,(6,10))+4,44:idx(42)+coded(2,(2,1,27))}
 # The existing inspector supplies table0..10 offsets. Extend by ECMA row sizes.
 p=m.starts[10]+m.rows[10]*m.sizes[10];starts={}
 for table in range(11,45):
  starts[table]=p;p+=m.rows.get(table,0)*sizes[table]
 root=0x5fbf1c;q=(root+16+u32(root+12)+3)&~3;count=u16(q+2);q+=4;streams={}
 for _ in range(count):
  off,length=u32(q),u32(q+4);e=b.index(0,q+8,q+128)
  streams[b[q+8:e].decode()]=(root+off,length);q=(e+4)&~3
 if streams['#~'][0]+streams['#~'][1]-p!=2:raise ValueError('metadata table boundary changed')
 width=coded(1,(6,10));row=starts[43]+(0x16a0-1)*sizes[43]
 target=u16(row) if width==2 else u32(row)
 symbol=m.fq((0x0a000000 if target&1 else 0x06000000)|(target>>1))
 def compressed(pos):
  x=b[pos]
  if x<128:return x,pos+1
  if x<192:return ((x&63)<<8)|b[pos+1],pos+2
  if x<224:return ((x&31)<<24)|(b[pos+1]<<16)|(b[pos+2]<<8)|b[pos+3],pos+4
  raise ValueError('invalid compressed integer')
 length,pos=compressed(streams['#Blob'][0]+u32(row+width));end=pos+length
 if b[pos:pos+3]!=bytes((0x0a,1,0x12)):raise ValueError('expected one class generic argument')
 typ,pos=compressed(pos+3)
 if pos!=end or typ&3:raise ValueError('expected exact TypeDef argument')
 argument=m.typedef[(typ>>2)-1][0]
 code=m.body(m.methods[0xaa22-1][0]);calls=decode_calls(code)
 def call_at(pc):return next((m.fq(t) for p,_,t in calls if p==pc),None)
 def branch(pc):
  if code[pc]!=0x3a:raise ValueError('expected brtrue')
  return pc+5+int.from_bytes(code[pc+1:pc+5],'little',signed=True)
 checks={
  'configuration_parser':symbol=='WNEngine.JsonTool.Deserialize',
  'configuration_type':argument=='WNLogin.VersionCustomRoot',
  'null_local_before_parse':code[0xcd:0xd0]==bytes((0x14,0x13,7)),
  'empty_settings_guard':call_at(0xd2)=='System.String.IsNullOrEmpty',
  'empty_bypasses_parser':branch(0xd7)==0x111,
  'parser_call':any(p==0xde and t==0x2b0016a0 for p,_,t in calls),
  'same_local_null_guard':code[0x111:0x113]==bytes((0x11,7)) and branch(0x113)==0x11f,
  'fallback_constructor':call_at(0x118)=='WNLogin.VersionCustomRoot..ctor' and code[0x11d:0x11f]==bytes((0x13,7)),
 }
 if not all(checks.values()):raise ValueError('managed source checks failed: '+','.join(k for k,v in checks.items() if not v))
 return checks
