#!/usr/bin/env python3
"""Prepare private APK controls from the owner's original; never install/run.

Python stdlib, openssl and Java required. Downloads only the pinned Android
signer JAR (~1 MB), never an APK/XAPK. Default source/host reads use paired adb.
"""
import argparse, datetime, hashlib, json, os, re, secrets, shutil, struct
import subprocess, sys, urllib.request, uuid, zipfile, zlib
from pathlib import Path

APK_SHA='33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9'
DLL_SHA='174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9'
JAR_SHA='00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7'
SDK_URL='https://dl.google.com/android/repository/build-tools_r35_linux.zip'
PACKAGE='com.tencent.tmgp.cfmnac'
HOST_FINGERPRINTS={
 '19f2e13a8c85347201f8a5a29379aa6aa9f67832eb7a5ab68d82feb6e87e0cdf',
 '343bca6e1806f447beb7f69f782ebc61f5fc51bfeb7cc80623160853098a413f',
 '4e3834c9262fd9aff98a57d4f3c0ef73a5e607872d2e29887184ae618496e7b5',
 '888616555cd0bf7774c9baa3b122928878092efb87c0654b5c4c577ee542c9e4',
 'c9bd0b5ed80e90ce9ea695ffe00d9337cb86624d4fd2630a04ff257f91276c15',
 'd19ee0dbbe0dd953c90728803cbb31333a6a5b592e0423d6850dc0898da82d81',
 'dca2d537d9d44611edc2d220718f125f4c6bc2bfdd2d333a2235ae886e40fddd'}

def digest(raw):return hashlib.sha256(raw).hexdigest()

def run(args,expected=0):
    try:r=subprocess.run([str(x) for x in args],capture_output=True,timeout=90)
    except (OSError,subprocess.TimeoutExpired):raise ValueError('Required offline tool failed or timed out.') from None
    if r.returncode!=expected:raise ValueError('Offline command failed: '+str(args[0]).split('/')[-1]+'; no raw output exported.')
    return r.stdout

def source_bytes(source):
    if source:
        source=Path(source)
        if source.stat().st_size<=40*1024*1024:
            raw=source.read_bytes()
            if digest(raw)==APK_SHA:return raw
        # Read only bounded APK entries; never unpack the XAPK/OBB/assets.
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                if info.filename.endswith('.apk') and info.file_size<=40*1024*1024:
                    raw=archive.read(info)
                    if digest(raw)==APK_SHA:return raw
        raise ValueError('Source does not contain the exact original APK.')
    lines=run(['adb','shell','pm','path',PACKAGE]).decode('utf8').splitlines()
    names=[x.removeprefix('package:').strip() for x in lines if x.startswith('package:') and x.endswith('/base.apk')]
    if len(names)!=1 or not re.fullmatch(r'/data/app/[A-Za-z0-9_./=~+\-]+\.apk',names[0]):
        raise ValueError('Installed APK path unavailable; use --source with your original APK/XAPK.')
    raw=run(['adb','exec-out','cat',names[0]])
    if len(raw)>40*1024*1024 or digest(raw)!=APK_SHA:
        raise ValueError('Installed APK differs from exact original; use --source with original APK/XAPK.')
    return raw

def allowed_hosts(values):
    values=sorted(set(h.lower().rstrip('.') for h in values))
    if not values or len(values)>7:raise ValueError('No bounded original SDK hostname scope available.')
    for host in values:
        if not re.fullmatch(r'[a-z0-9.-]+\.[a-z]{2,}',host) or digest(host.encode('ascii')) not in HOST_FINGERPRINTS:
            raise ValueError('Hostname is outside pinned original SDK scope.')
    return values

def hosts_from_adb():
    pid=run(['adb','shell','pidof','-s',PACKAGE]).strip()
    if not re.fullmatch(rb'[1-9][0-9]{0,8}',pid):raise ValueError('Game must remain running for the existing-log read.')
    raw=run(['adb','logcat','-d','-t','1500','--pid='+pid.decode('ascii'),'-v','brief'])
    if len(raw)>8*1024*1024:raise ValueError('Log buffer exceeds bound.')
    values=[]
    for line in raw.decode('utf8',errors='replace').splitlines():
        if not re.match(r'^[VDIWEF]/iMSDK\s*\(\s*\d+\s*\):',line):continue
        for host in re.findall(r'''Unable to resolve host\s+\\?["']([A-Za-z0-9.-]{1,253})\\?["']''',line,re.I):
            host=host.lower().rstrip('.')
            if digest(host.encode('ascii')) in HOST_FINGERPRINTS:values.append(host)
    return allowed_hosts(values)

def signer_jar(out,local=None):
    target=out/'apksigner.jar'
    if local:raw=Path(local).read_bytes()
    else:
        print('Downloading pinned signing tool (~1 MB); no game download.')
        request=urllib.request.Request(SDK_URL,headers={'Range':'bytes=8177106-9156442','Accept-Encoding':'identity'})
        with urllib.request.urlopen(request,timeout=30) as response:
            if response.status!=206 or not response.headers.get('Content-Range','').startswith('bytes 8177106-9156442/'):
                raise ValueError('Server did not honor bounded tool download; no full archive downloaded.')
            compressed=response.read(979338)
        if len(compressed)!=979337:raise ValueError('Incomplete signer download.')
        decoder=zlib.decompressobj(-15)
        raw=decoder.decompress(compressed,2*1024*1024+1)
        if len(raw)>2*1024*1024 or not decoder.eof or decoder.unconsumed_tail:
            raise ValueError('Signer decompression exceeds the bound or is incomplete.')
    if digest(raw)!=JAR_SHA:raise ValueError('Signer fingerprint mismatch.')
    target.write_bytes(raw);return target

def signature(name):
    return name.startswith('META-INF/') and (name.upper().endswith(('.RSA','.DSA','.EC','.SF','.MF')) or name.startswith('META-INF/SIG-'))

def write_apk(original,payload,path):
    import io,copy
    with zipfile.ZipFile(io.BytesIO(original)) as source,zipfile.ZipFile(path,'w') as output:
        names=set()
        for old in source.infolist():
            if old.filename not in payload:continue
            info=copy.copy(old)
            if info.compress_type==zipfile.ZIP_STORED:
                offset=output.fp.tell()+30+len(info.filename.encode('utf8'))+len(info.extra)
                if offset%4:
                    pad=-(offset+4)%4
                    info.extra+=struct.pack('<HH',0xd935,pad)+bytes(pad)
            output.writestr(info,payload[info.filename]);names.add(info.filename)
        for name in sorted(payload.keys()-names):
            output.writestr(name,payload[name],compress_type=zipfile.ZIP_DEFLATED)

def verify_payload(path,expected):
    with zipfile.ZipFile(path) as archive:
        if len(archive.namelist())!=len(set(archive.namelist())):raise ValueError('Duplicate APK entries.')
        found={i.filename:archive.read(i) for i in archive.infolist() if not signature(i.filename)}
        if found!=expected:raise ValueError('APK payload mismatch.')
        with path.open('rb') as stream:
            for i in archive.infolist():
                if i.compress_type==zipfile.ZIP_STORED:
                    stream.seek(i.header_offset);header=stream.read(30)
                    n,e=struct.unpack_from('<HH',header,26)
                    if (i.header_offset+30+n+e)%4:raise ValueError('APK stored-entry alignment failed.')

def certificates(out,hosts):
    for name,ca in [('apk-signing',False),('local-ca',True),('wrong-ca',True)]:
        args=['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','90','-subj','/CN=CF18-'+name,'-keyout',out/(name+'.key.pem'),'-out',out/(name+'.pem')]
        if ca:args+=['-addext','basicConstraints=critical,CA:TRUE,pathlen:0','-addext','keyUsage=critical,keyCertSign,cRLSign']
        run(args)
    run(['openssl','pkcs8','-topk8','-nocrypt','-in',out/'apk-signing.key.pem','-outform','DER','-out',out/'apk-signing.key.der'])
    ext=out/'private-server-extensions.cnf'
    ext.write_text('basicConstraints=CA:FALSE\nextendedKeyUsage=serverAuth\nsubjectAltName='+','.join('DNS:'+h for h in hosts)+'\n')
    for name,ca in [('local-server','local-ca'),('wrong-server','wrong-ca')]:
        run(['openssl','req','-new','-newkey','rsa:2048','-nodes','-subj','/CN=CF18-local-server','-keyout',out/(name+'.key.pem'),'-out',out/(name+'.csr')])
        run(['openssl','x509','-req','-days','90','-in',out/(name+'.csr'),'-CA',out/(ca+'.pem'),'-CAkey',out/(ca+'.key.pem'),'-set_serial','0x'+secrets.token_hex(16),'-extfile',ext,'-out',out/(name+'.pem')])
    run(['openssl','verify','-CAfile',out/'local-ca.pem',out/'local-server.pem'])
    run(['openssl','verify','-CAfile',out/'local-ca.pem',out/'wrong-server.pem'],expected=2)

def prepare(raw,hosts,out,jar):
    import io
    if digest(raw)!=APK_SHA:raise ValueError('Exact original APK required.')
    helper={};exec(RESOURCE_SOURCE,helper)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if len(archive.namelist())!=len(set(archive.namelist())):raise ValueError('Duplicate source entries.')
        original={i.filename:archive.read(i) for i in archive.infolist() if not signature(i.filename)}
    dll=[v for k,v in original.items() if k.lower().endswith('/assembly-csharp.dll')]
    if len(dll)!=1 or digest(dll[0])!=DLL_SHA:raise ValueError('Protected DLL fingerprint mismatch.')
    arsc,xid,cid=helper['append_resources'](original['resources.arsc'])
    manifest=helper['manifest_reference'](original['AndroidManifest.xml'],xid)
    certificates(out,hosts)
    candidate=dict(original);candidate.update({'AndroidManifest.xml':manifest,'resources.arsc':arsc,'res/xml/cf18_scoped_trust.xml':helper['trust_xml'](hosts,cid),'res/raw/cf18_local_ca.pem':(out/'local-ca.pem').read_bytes()})
    hashes={}
    for name,expected in [('signature_only',original),('scoped_trust',candidate)]:
        unsigned=out/(name+'.unsigned.apk');signed=out/(name+'.apk')
        write_apk(raw,expected,unsigned)
        run(['java','-jar',jar,'sign','--key',out/'apk-signing.key.der','--cert',out/'apk-signing.pem','--min-sdk-version','14','--v1-signing-enabled','true','--v2-signing-enabled','true','--v3-signing-enabled','false','--v4-signing-enabled','false','--out',signed,unsigned])
        run(['java','-jar',jar,'verify','--min-sdk-version','14',signed]);verify_payload(signed,expected)
        hashes[name]=digest(signed.read_bytes())
    return {'format':'CF2018_PRIVATE_APK_PREPARATION','source_sha256':APK_SHA,'protected_dll_sha256':DLL_SHA,
            'original_payload_entries':len(original),'control_changed_original_entries':0,
            'candidate_changed_original_entries':['AndroidManifest.xml','resources.arsc'],
            'candidate_added_entries':['res/xml/cf18_scoped_trust.xml','res/raw/cf18_local_ca.pem'],
            'scoped_host_count':len(hosts),'signatures_and_payload_verified':True,'stored_entries_aligned':True,
            'offline_correct_ca_accepted_wrong_ca_rejected':True,'android_runtime_tested':False,
            'phone_installation_performed':False,'apk_hashes':hashes}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,help='optional original APK/XAPK; otherwise read installed APK via adb')
    p.add_argument('--hosts-file',type=Path,help='private original-host JSON list; otherwise read existing SDK DNS logs via adb')
    p.add_argument('--signer-jar',type=Path,help='optional cached exact official signer')
    p.add_argument('--output-root',type=Path,default=Path.home()/'cf2018_private_apk_controls')
    p.add_argument('--report-dir',type=Path,default=Path.home()/'storage/downloads')
    a=p.parse_args();os.umask(0o077)
    try:
        if not shutil.which('openssl') or not shutil.which('java'):
            raise ValueError('Java and openssl required. In Termux install openjdk-17 and openssl-tool first.')
        print('Checking original source and existing SDK host scope; no game launch or installation.')
        raw=source_bytes(a.source)
        hosts=allowed_hosts(json.loads(a.hosts_file.read_text())) if a.hosts_file else hosts_from_adb()
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:8]
        out=a.output_root/stamp;out.mkdir(parents=True,mode=0o700,exist_ok=False)
        jar=signer_jar(out,a.signer_jar)
        result=prepare(raw,hosts,out,jar)
        (out/'verification_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        report=a.report_dir/('CF2018_APK_PREPARATION_'+stamp+'.txt')
        with report.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
        print('Offline preparation complete. Private APKs/keys remain under '+str(out))
        print('Share only this sanitized report: '+str(report))
        print('Do not install either APK yet. No installation or login was performed.')
        return 0
    except (ValueError,OSError,zipfile.BadZipFile) as error:
        if isinstance(error,ValueError):print(str(error),file=sys.stderr)
        else:print('Preparation stopped: source/tool/output access failed; no raw contents exported.',file=sys.stderr)
        return 1

# Embedded stdlib utility is inserted during packaging, with no original data.
RESOURCE_SOURCE = '"""Append isolated Android resources and one binary-manifest attribute.\n\nNo bytecode/native/asset rewriting. Callers must separately verify all original\nresource values, original ZIP payload hashes and signatures before using output.\n"""\nimport struct\n\nU32 = lambda b, p: struct.unpack_from(\'<I\', b, p)[0]\nU16 = lambda b, p: struct.unpack_from(\'<H\', b, p)[0]\nNONE = 0xffffffff\n\n\ndef chunk(kind, header, body):\n    return struct.pack(\'<HHI\', kind, 8 + len(header), 8 + len(header) + len(body)) + header + body\n\n\ndef chunks(raw, start):\n    p = start\n    while p < len(raw):\n        if p + 8 > len(raw):\n            raise ValueError(\'truncated chunk header\')\n        kind, head, size = struct.unpack_from(\'<HHI\', raw, p)\n        if not 8 <= head <= size or p + size > len(raw):\n            raise ValueError(\'invalid chunk bounds\')\n        yield p, kind, raw[p:p + size]\n        p += size\n    if p != len(raw):\n        raise ValueError(\'chunk boundary\')\n\n\ndef pool_values(raw):\n    if U16(raw, 0) != 1 or U16(raw, 2) != 28:\n        raise ValueError(\'unsupported string pool\')\n    count, styles, flags, begin, style_begin = struct.unpack_from(\'<5I\', raw, 8)\n    def length(p, utf8):\n        x = raw[p] if utf8 else U16(raw, p)\n        step, mask = (1, 0x80) if utf8 else (2, 0x8000)\n        p += step\n        if x & mask:\n            x = ((x & (mask - 1)) << (8 if utf8 else 16)) | (raw[p] if utf8 else U16(raw, p))\n            p += step\n        return x, p\n    values = []\n    for i in range(count):\n        p = begin + U32(raw, 28 + 4 * i)\n        size, p = length(p, bool(flags & 0x100))\n        if flags & 0x100:\n            size, p = length(p, True)\n            values.append(raw[p:p + size].decode(\'utf8\'))\n        else:\n            values.append(raw[p:p + 2 * size].decode(\'utf-16le\', errors=\'surrogatepass\'))\n    offsets = raw[28 + 4 * count:28 + 4 * (count + styles)]\n    style_data = raw[style_begin:] if style_begin else b\'\'\n    return values, offsets, style_data, flags\n\n\ndef make_pool(values, style_offsets=b\'\', style_data=b\'\', flags=0):\n    data, offsets = bytearray(), []\n    for text in values:\n        encoded = text.encode(\'utf-16le\', errors=\'surrogatepass\')\n        n = len(encoded) // 2\n        offsets.append(len(data))\n        data += struct.pack(\'<H\', n) if n < 0x8000 else struct.pack(\'<HH\', 0x8000 | (n >> 16), n & 0xffff)\n        data += encoded + b\'\\0\\0\'\n    data += b\'\\0\' * (-len(data) % 4)\n    begin = 28 + 4 * len(values) + len(style_offsets)\n    header = struct.pack(\'<5I\', len(values), len(style_offsets) // 4, flags & ~0x101,\n                         begin, begin + len(data) if style_data else 0)\n    return chunk(1, header, b\'\'.join(struct.pack(\'<I\', o) for o in offsets) + style_offsets + data + style_data)\n\n\ndef extend_pool(raw, additions):\n    values, offsets, styles, flags = pool_values(raw)\n    return make_pool(values + additions, offsets, styles, flags), len(values)\n\n\ndef append_resources(raw):\n    if U16(raw, 0) != 2 or U32(raw, 8) != 1 or U32(raw, 4) != len(raw):\n        raise ValueError(\'single exact resource package required\')\n    parts = list(chunks(raw, U16(raw, 2)))\n    if [kind for _, kind, _ in parts] != [1, 0x200]:\n        raise ValueError(\'unexpected resource top-level chunks\')\n    global_pool, string_index = extend_pool(parts[0][2], [\'res/xml/cf18_scoped_trust.xml\', \'res/raw/cf18_local_ca.pem\'])\n    package = parts[1][2]\n    head = U16(package, 2)\n    if head != 288 or U32(package, 8) != 0x7f or U32(package, 284):\n        raise ValueError(\'unsupported package identity/offset\')\n    type_at, key_at = U32(package, 268), U32(package, 276)\n    sub = list(chunks(package, head))\n    type_raw = next(c for p, _, c in sub if p == type_at)\n    key_raw = next(c for p, _, c in sub if p == key_at)\n    names = pool_values(type_raw)[0]\n    if \'cf18trustxml\' in names or \'cf18trustcert\' in names or len(names) > 252:\n        raise ValueError(\'resource type collision/budget\')\n    new_types, type_index = extend_pool(type_raw, [\'cf18trustxml\', \'cf18trustcert\'])\n    new_keys, key_index = extend_pool(key_raw, [\'cf18_scoped_trust\', \'cf18_local_ca\'])\n    result, offsets = bytearray(), {}\n    for p, _, c in sub:\n        offsets[p] = head + len(result)\n        result += new_types if p == type_at else new_keys if p == key_at else c\n    ids = []\n    for i in range(2):\n        tid = type_index + i + 1\n        ids.append(0x7f000000 | tid << 16)\n        # One default configuration and one file entry in each new custom type.\n        result += chunk(0x202, struct.pack(\'<BBHI\', tid, 0, 0, 1), struct.pack(\'<I\', 0))\n        config = struct.pack(\'<I\', 64) + bytes(60)\n        header = struct.pack(\'<BBHII\', tid, 0, 0, 1, 8 + 12 + len(config) + 4) + config\n        entry = struct.pack(\'<HHI\', 8, 0, key_index + i) + struct.pack(\'<HBBI\', 8, 0, 3, string_index + i)\n        result += chunk(0x201, header, struct.pack(\'<I\', 0) + entry)\n    ph = bytearray(package[:head])\n    struct.pack_into(\'<I\', ph, 4, head + len(result))\n    struct.pack_into(\'<I\', ph, 268, offsets[type_at])\n    struct.pack_into(\'<I\', ph, 276, offsets[key_at])\n    # All original IDs and type-entry chunks remain intact.\n    out = chunk(2, struct.pack(\'<I\', 1), global_pool + ph + result)\n    return out, ids[0], ids[1]\n\n\ndef manifest_reference(raw, xml_id):\n    if U16(raw, 0) != 3 or U32(raw, 4) != len(raw):\n        raise ValueError(\'binary manifest required\')\n    parts = list(chunks(raw, U16(raw, 2)))\n    pools = [c for _, k, c in parts if k == 1]\n    if len(pools) != 1:\n        raise ValueError(\'manifest string pool count\')\n    values = pool_values(pools[0])[0]\n    if \'networkSecurityConfig\' in values:\n        raise ValueError(\'existing trust configuration requires review\')\n    new_pool, index = extend_pool(pools[0], [\'networkSecurityConfig\'])\n    android = values.index(\'http://schemas.android.com/apk/res/android\')\n    output, modified, maps = [], 0, 0\n    for _, kind, c in parts:\n        if kind == 1:\n            c = new_pool\n        elif kind == 0x180:\n            ids = list(struct.unpack(\'<\' + \'I\' * ((len(c) - 8) // 4), c[8:]))\n            ids += [0] * (index + 1 - len(ids))\n            ids[index] = 0x01010527  # framework android:networkSecurityConfig\n            c = chunk(kind, b\'\', struct.pack(\'<\' + \'I\' * len(ids), *ids))\n            maps += 1\n        elif kind == 0x102 and values[U32(c, 20)] == \'application\':\n            start, size, count = struct.unpack_from(\'<HHH\', c, 24)\n            if size != 20:\n                raise ValueError(\'manifest attribute layout\')\n            end = 16 + start + size * count\n            attribute = struct.pack(\'<IIIHBBI\', android, index, NONE, 8, 0, 1, xml_id)\n            c = bytearray(c[:end] + attribute + c[end:])\n            struct.pack_into(\'<I\', c, 4, len(c))\n            struct.pack_into(\'<H\', c, 28, count + 1)\n            modified += 1\n        output.append(c)\n    if modified != 1 or maps != 1:\n        raise ValueError(\'manifest application/resource-map count\')\n    return chunk(3, b\'\', b\'\'.join(output))\n\n\ndef trust_xml(hosts, certificate_id):\n    import re\n    if not hosts or len(hosts) > 8 or any(not re.fullmatch(r\'[a-z0-9.-]+\\.[a-z]{2,}\', h) for h in hosts):\n        raise ValueError(\'bounded original SDK DNS hosts required\')\n    strings = [\'network-security-config\', \'base-config\', \'trust-anchors\', \'certificates\',\n               \'src\', \'system\', \'domain-config\', \'domain\', \'includeSubdomains\', \'false\'] + list(hosts)\n    ix = {s: i for i, s in enumerate(strings)}\n    data = bytearray(make_pool(strings))\n    def node(kind, body):\n        data.extend(chunk(kind, struct.pack(\'<II\', 1, NONE), body))\n    def start(name, attributes=()):\n        attrs = b\'\'.join(struct.pack(\'<IIIHBBI\', NONE, ix[key], ix[value] if typ == 3 else NONE,\n                                    8, 0, typ, ix[value] if typ == 3 else value) for key, typ, value in attributes)\n        node(0x102, struct.pack(\'<IIHHHHHH\', NONE, ix[name], 20, 20, len(attributes), 0, 0, 0) + attrs)\n    def end(name):\n        node(0x103, struct.pack(\'<II\', NONE, ix[name]))\n    start(\'network-security-config\');start(\'base-config\');start(\'trust-anchors\')\n    start(\'certificates\', [(\'src\', 3, \'system\')]);end(\'certificates\')\n    end(\'trust-anchors\');end(\'base-config\');start(\'domain-config\')\n    for host in hosts:\n        start(\'domain\', [(\'includeSubdomains\', 0x12, 0)])\n        node(0x104, struct.pack(\'<IHBBI\', ix[host], 8, 0, 3, ix[host]))\n        end(\'domain\')\n    start(\'trust-anchors\');start(\'certificates\', [(\'src\', 1, certificate_id)]);end(\'certificates\')\n    end(\'trust-anchors\');end(\'domain-config\');end(\'network-security-config\')\n    return chunk(3, b\'\', data)\n'

if __name__=='__main__':sys.exit(main())
