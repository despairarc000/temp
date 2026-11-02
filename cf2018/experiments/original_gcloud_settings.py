"""Exact-build read-only settings audit; returns counts/labels, never values.

The small CIL control interprets only the source selection method on synthetic
strings. It is not CLR execution, preference discovery or phone acceptance.
"""
import csv,hashlib,io,re,struct
from original_bundle_manifest import DLL_SHA,_decode_asset
RESOURCE_SHA='bc00133a6bc82a6430dbe5d0ffaf96e6e7e9c883f697fa148180c1d1c1c6dd0b'
PAYLOAD_SHA='9a4bbf9944086d0abad651dce14a30fbd7ab111413ded74fd6682403e0553f15'

def _body(metadata,rid):
    if metadata.sha!=DLL_SHA:raise ValueError('exact original managed source required')
    return metadata.body(metadata.methods[rid-1][0])

def evaluate_get_value(metadata,default,regional):
    """Bounded original GetValueString CIL, with synthetic field/string inputs."""
    code=_body(metadata,0x2b61);b=metadata.b;fields={}
    for rid in range(1,metadata.rows[4]+1):
        at=metadata.starts[4]+(rid-1)*metadata.sizes[4]+2
        name=metadata.str_at(struct.unpack_from('<I',b,at)[0])
        if name in ('m_DefaultValue','m_Value'):fields[0x04000000|rid]=name
    values={'m_DefaultValue':default,'m_Value':regional};stack=[];local={};pc=0
    for _ in range(64):
        if not 0<=pc<len(code):raise ValueError('source instruction bound')
        op=code[pc];pc+=1
        if op==0x02:stack.append(values)
        elif op==0x7b:
            token=int.from_bytes(code[pc:pc+4],'little');pc+=4
            name=fields.get(token)
            if name not in values:raise ValueError('unexpected source field')
            stack.append(stack.pop()[name])
        elif op==0x28:
            token=int.from_bytes(code[pc:pc+4],'little');pc+=4
            if metadata.fq(token)!='System.String.IsNullOrEmpty':raise ValueError('unexpected source call')
            stack.append(stack.pop() in (None,''))
        elif op in (0x38,0x39):
            offset=int.from_bytes(code[pc:pc+4],'little',signed=True);pc+=4
            if op==0x38 or not stack.pop():pc+=offset
        elif op==0x0a:local[0]=stack.pop()
        elif op==0x06:stack.append(local[0])
        elif op==0x2a:
            if len(stack)!=1:raise ValueError('unexpected source return stack')
            return stack.pop()
        else:raise ValueError('unhandled source instruction')
    raise ValueError('source instruction budget')

def audit(metadata,raw,decode_calls):
    _body(metadata,0x229)
    if type(raw) is not bytes or hashlib.sha256(raw).hexdigest()!=RESOURCE_SHA:
        raise ValueError('exact original resource required')
    import UnityPy
    env=UnityPy.load(raw)
    if len(env.objects)!=1:raise ValueError('resource object count changed')
    obj=env.objects[0]
    if obj.path_id!=1 or obj.type.name!='TextAsset':raise ValueError('resource reference changed')
    asset=obj.read()
    if asset.m_Name!='GcloudSetting_':raise ValueError('resource identity changed')
    payload=asset.m_Script
    if isinstance(payload,str):payload=payload.encode('utf8',errors='surrogateescape')
    plain=_decode_asset(metadata,payload,PAYLOAD_SHA)
    rows=list(csv.reader(io.StringIO(plain.decode('utf-8-sig'))))
    if len(rows)!=24 or any(len(r)!=20 for r in rows):raise ValueError('CSV dimensions changed')
    labels=rows[0]
    if labels[:3]!=['Key','Comment','Default']:raise ValueError('CSV schema changed')
    # First record is the column descriptor, skipped by the original reader.
    settings={r[0]:r for r in rows[2:]}
    if len(settings)!=22:raise ValueError('CSV setting identity/count changed')
    def calls(rid):
        result=decode_calls(_body(metadata,rid))
        if result is None:raise ValueError('source operand walk failed')
        return {(pc,metadata.fq(token)) for pc,_,token in result}
    source={
        'reader_uses_asset_bytes':(0x159,'UnityEngine.TextAsset.get_bytes') in calls(0x229),
        'reader_uses_source_decoder':(0x168,'WNEngine.AESHelper.AESDecrypt') in calls(0x229),
        'regional_field_uses_current_language':(0x48,'PlatformDef.get_CurrentLanguage') in calls(0x2b5b),
        'regional_field_uses_formatted_column':(0x4d,'System.String.Format') in calls(0x2b5b),
        'regional_field_read':(0x59,'WNEngine.BaseSystemConfigData.ReadString') in calls(0x2b5b),
    }
    if not all(source.values()):raise ValueError('settings source checks changed')
    row=settings['THIRD_TVERSION_SERVER']
    dns=lambda s:bool(re.fullmatch(r'[A-Za-z0-9.-]+\.[A-Za-z]{2,}',s))
    return {'resource_objects':1,'payload_bytes':len(payload),'plaintext_bytes':len(plain),
            'csv_rows':len(rows),'csv_columns':20,'setting_rows':len(settings),
            'regional_columns':len(labels)-3,'tversion_default_empty':row[2]=='',
            'tversion_regional_dns_raw':sum(dns(x) for x in row[3:]),
            'tversion_regional_dns_after_strip':sum(dns(x.strip()) for x in row[3:]),
            'source_checks':source}
