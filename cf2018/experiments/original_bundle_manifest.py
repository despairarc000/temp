"""Read-only, exact-build manifest audit; no key or original data export.

Asset decoding parameters are resolved in memory from the supplied hash-checked
managed inspector. Only record counts/reference labels are returned. Requires
optional cryptography and UnityPy, not required by the server or phone tools.
"""
import hashlib,struct
DLL_SHA='174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9'
BUNDLE_SHA='cc3c71bd875d5d747675290a99b4fe40cf904e685e2210df10a7a64371b1dfd8'

def _decode_asset(metadata,ciphertext,expected_sha):
    if metadata.sha!=DLL_SHA:raise ValueError('exact original managed source required')
    if type(ciphertext) is not bytes or hashlib.sha256(ciphertext).hexdigest()!=expected_sha:
        raise ValueError('exact original configuration entry required')
    b=metadata.b;u16=lambda p:struct.unpack_from('<H',b,p)[0]
    u32=lambda p:struct.unpack_from('<I',b,p)[0]
    root=0x5fbf1c;p=(root+16+u32(root+12)+3)&~3;count=u16(p+2);p+=4;us=None
    for _ in range(count):
        offset,length=u32(p),u32(p+4);end=b.index(0,p+8,p+128)
        if b[p+8:end]==b'#US':us=root+offset
        p=(end+4)&~3
    if us is None:raise ValueError('missing metadata string heap')
    def parameter(rid,width):
        code=metadata.body(metadata.methods[rid-1][0])
        if len(code)!=6 or code[0]!=0x72 or code[-1]!=0x2a:
            raise ValueError('source getter shape changed')
        token=int.from_bytes(code[1:5],'little')
        if token>>24!=0x70:raise ValueError('expected source string reference')
        q=us+(token&0xffffff);x=b[q];q+=1
        if x<128:length=x
        elif x<192:length=((x&63)<<8)|b[q];q+=1
        else:length=((x&31)<<24)|(b[q]<<16)|(b[q+1]<<8)|b[q+2];q+=3
        if not 1<=length<=256:raise ValueError('source parameter length bound')
        return b[q:q+length-1].decode('utf-16le').ljust(width).encode('utf8')[:width]
    from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
    decoder=Cipher(algorithms.AES(parameter(0x26be,32)),modes.CBC(parameter(0x26bf,16))).decryptor()
    plain=decoder.update(ciphertext)+decoder.finalize();padding=plain[-1]
    if not 1<=padding<=16 or plain[-padding:]!=bytes([padding])*padding:
        raise ValueError('configuration padding invalid')
    plain=plain[:-padding]
    return plain

def summarize(metadata,ciphertext):
    plain=_decode_asset(metadata,ciphertext,BUNDLE_SHA)
    if not plain.startswith((b'UnityFS\0',b'UnityRaw\0',b'UnityWeb\0')):
        raise ValueError('configuration bundle signature invalid')
    import UnityPy
    env=UnityPy.load(plain);scripts=[]
    for obj in env.objects:
        if obj.type.name=='MonoScript':
            value=obj.read()
            if value.m_Namespace=='WNEngine' and value.m_ClassName=='ABInfoJsonCfg':scripts.append(obj.path_id)
    if len(scripts)!=1:raise ValueError('manifest script identity changed')
    byid={obj.path_id:obj for obj in env.objects};rows=[]
    for obj in env.objects:
        if obj.type.name!='AssetBundle':continue
        for name,entry in obj.read().m_Container:
            item=byid.get(entry.asset.m_PathID)
            if item is None or item.type.name!='MonoBehaviour':continue
            raw=item.get_raw_data()
            # Exact Unity4 player layout, including the source script reference.
            if struct.unpack_from('<ii',raw,12)!=(0,scripts[0]):
                raise ValueError('manifest script reference mismatch')
            pos=[20]
            def integer():
                if pos[0]+4>len(raw):raise ValueError('manifest truncation')
                value=struct.unpack_from('<i',raw,pos[0])[0];pos[0]+=4;return value
            def string():
                length=integer()
                if not 0<=length<=4096 or pos[0]+length>len(raw):raise ValueError('manifest string bound')
                value=raw[pos[0]:pos[0]+length].decode('utf8');pos[0]=(pos[0]+length+3)&~3
                return value
            def array():
                size=integer()
                if not 0<=size<=20000:raise ValueError('manifest array bound')
                return [string() for _ in range(size)]
            if string().lower()!=name:raise ValueError('manifest name mismatch')
            size=integer()
            if not 0<=size<=20000:raise ValueError('manifest record bound')
            matches=0
            for _ in range(size):
                integer();asset=string();array();array();array()
                matches+=int('gcloudsetting' in asset.lower())
            local=array()
            if pos[0]!=len(raw):raise ValueError('manifest trailing bytes')
            rows.append({'manifest':name,'assets':size,'local_bundles':len(local),
                         'gcloud_name_matches':matches,'full_consumption':True})
    return {'bundle_objects':len(env.objects),'manifests':rows,
            'asset_records':sum(r['assets'] for r in rows),
            'local_bundle_records':sum(r['local_bundles'] for r in rows)}
