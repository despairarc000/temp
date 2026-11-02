"""Bounded synthetic startup-directory result. No sockets or credential handling.

Uses the build's source-selected configuration node and empty application data,
which exercises the original VersionCustomRoot default-constructor path.
"""
METHOD=b'DirService:get_server_dirtree_by_id'
ROUTE=b'DirService'
NODE_ID=0x01010100

def vi(n):
 if type(n) is not int or not 0<=n<2**64:raise ValueError('bounded unsigned value')
 b=bytearray()
 while n>=128:b.append((n&127)|128);n>>=7
 return bytes(b)+bytes([n])
def field(n,k,v):
 tag=vi(n<<4|k)
 if k==0:return tag+vi(v)
 if k==1 and type(v) is int and 0<=v<=255:return tag+bytes([v])
 if k==5 and type(v) is bytes and len(v)<=2048:return tag+len(v).to_bytes(4,'big')+v
 raise ValueError('TLV field shape')
def node():
 custom=field(1,0,0)+field(2,0,0)+field(3,5,b'')
 category=field(1,0,0)+field(2,0,NODE_ID<<1)+field(3,0,0)+field(4,5,b'')+field(5,0,0)+field(6,5,custom)
 content=field(1,0,0)+field(2,5,field(0,5,category))
 return b'\xaa'+(5+len(content)).to_bytes(4,'big')+content

def thrift_field(kind,number,value):return bytes([kind])+number.to_bytes(2,'big')+value

def component():
 tree=thrift_field(8,1,(1).to_bytes(4,'big'))+thrift_field(11,2,len(node()).to_bytes(4,'big')+node())+thrift_field(15,3,b'\x0c'+bytes(4))+b'\0'
 result=thrift_field(8,1,bytes(4))+thrift_field(11,2,bytes(4))+thrift_field(15,3,b'\x0c'+(1).to_bytes(4,'big')+tree)+b'\0'
 return thrift_field(12,0,result)+b'\0'

def rpc(sequence):
 if type(sequence) is not int or not 0<=sequence<2**64:raise ValueError('RPC u64 required')
 return len(METHOD).to_bytes(4,'big')+METHOD+b'\x02'+sequence.to_bytes(8,'big')+component()

def request_correlation(frame):
 from directory_identify import classify_frame
 from routed_fingerprint_v21 import route_value_and_body
 from tgcp_wire import fields,require_field
 d=classify_frame(frame,ROUTE)
 if d.get('directory_request')!='BY_ID_COMPLETE' or d.get('directory_encoding')!='LEGACY64':raise ValueError('complete original BY_ID legacy request required')
 end=2+int.from_bytes(frame[3:7],'big');base=fields(require_field(fields(frame[7:end]),1,5).value)
 packet_sequence=require_field(base,7,0).value
 _,body=route_value_and_body(frame)
 pos=4+4+len(METHOD)+1
 return packet_sequence,int.from_bytes(body[pos:pos+8],'big')

def make_candidate(frame):
 packet_seq,rpc_seq=request_correlation(frame)
 response=rpc(rpc_seq)
 # Same AA and DataHead family already exercised by the discovery response.
 # Server body starts at RPC header, not the client's 4B packet-sequence prefix.
 values=[0x4366,0,1,0x4013,0,0,packet_seq,0,len(response)]
 base=b''.join(field(i,1 if i==6 else 0,v) for i,v in enumerate(values,1))
 route=field(4,5,field(1,5,ROUTE))
 data=field(1,1,0)+field(2,1,0)+field(3,1,1)+field(4,5,route)
 header=field(1,5,base)+field(2,5,field(0x4013,5,data))
 wire=b'\xaa'+(5+len(header)).to_bytes(4,'big')+header+response
 if len(wire)>1024:raise ValueError('response size bound')
 return wire
