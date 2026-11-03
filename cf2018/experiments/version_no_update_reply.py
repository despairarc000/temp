"""Synthetic no-update candidate for a fully validated local version request.

No sockets, credential logic or logs. Request values remain in transient memory;
this is an offline-server experiment, not an original-server update verdict.
"""
def field(kind,ident,value):return bytes([kind])+ident.to_bytes(2,'big')+value
def string(ident,value=b''):return field(11,ident,len(value).to_bytes(4,'big')+value)

def response(frame):
    from version_discovery_control import classify_frame,METHOD
    from routed_fingerprint_v21 import route_value_and_body
    from tgcp_wire import fields,require_field
    from directory_config_reply import field as tag
    profile=classify_frame(frame)
    if profile['version_request']!='COMPLETE_LEGACY64' or profile['version_mode'] not in ('APPLICATION','RESOURCES'):raise ValueError('complete known version request required')
    _,body=route_value_and_body(frame)
    seqpos=4+4+len(METHOD)+1;rpcseq=body[seqpos:seqpos+8]
    p=seqpos+8
    # The classifier has proved the complete schema. Locate comm regardless of
    # valid field order; never infer scalar positions from body size alone.
    def struct():
        nonlocal p
        out={}
        while body[p]:
            start=p;kind=body[p];ident=int.from_bytes(body[p+1:p+3],'big');p+=3
            if kind==12:value=struct()
            elif kind==11:
                size=int.from_bytes(body[p:p+4],'big');p+=4;value=body[p:p+size];p+=size
            else:
                size={6:2,8:4,10:8}[kind];value=int.from_bytes(body[p:p+size],'big');p+=size
            out[ident]=(kind,value,body[start:p])
        p+=1;return out
    comm=struct()[1][1][1][1]
    product=comm[3][1];request_type=comm[4][1]
    if product not in (1,2) or request_type not in (1,2):raise ValueError('unsupported version product/request type')
    version=comm[5 if product==1 else 6][1]
    if version==0:raise ValueError('installed version missing')
    # Known shared response comm fields only; optional request platform fields
    # are not added to the response schema.
    echoed=b''.join(comm[i][2] for i in range(1,8))+b'\0'
    package=field(10,1,version.to_bytes(8,'big'))+b''.join(string(i) for i in range(2,7))+b'\0'
    info=field(12,1,package)+field(8,2,bytes(4))+b'\0'
    result=field(8,1,bytes(4))+field(12,2,echoed)+field(12,3,info)+b'\0'
    payload=len(METHOD).to_bytes(4,'big')+METHOD+b'\2'+rpcseq+field(12,0,result)+b'\0'
    end=2+int.from_bytes(frame[3:7],'big');base=fields(require_field(fields(frame[7:end]),1,5).value)
    packet=require_field(base,7,0).value
    values=[0x4366,0,1,0x4013,0,0,packet,0,len(payload)]
    headbase=b''.join(tag(i,1 if i==6 else 0,v) for i,v in enumerate(values,1))
    route=tag(4,5,tag(1,5,b'VersionUpdate'))
    data=tag(1,1,0)+tag(2,1,0)+tag(3,1,1)+tag(4,5,route)
    head=tag(1,5,headbase)+tag(2,5,tag(0x4013,5,data))
    wire=b'\xaa'+(5+len(head)).to_bytes(4,'big')+head+payload
    if len(wire)>4096:raise ValueError('response bound')
    return wire,profile['version_mode']
