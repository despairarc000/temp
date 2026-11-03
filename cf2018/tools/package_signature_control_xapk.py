#!/usr/bin/env python3
"""Repackage only the verified signature-only control into the owner's XAPK.
Creates a new archive/report; never downloads game files or installs anything.
"""
import copy,datetime,hashlib,json,shutil,uuid
from pathlib import Path,PurePosixPath
from zipfile import ZipFile

ORIGINAL='33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9'
CONTROL='e851f9f236afe2042f21acf2cd5bd74720d087800c35e4da94996f3fa89c2797'
APK_BYTES=30884905
OBB_BYTES=737048867

def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    h=Path.home();downloads=h/'storage/shared/Download'
    source=downloads/'Original.xapk'
    control=h/'cf2018_control_test/control.apk'
    payload=control.read_bytes()
    if sha(payload)!=CONTROL:raise ValueError('Control APK differs from reviewed phone report.')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:8]
    target=downloads/('CF2018_SIGNATURE_CONTROL_'+stamp+'.xapk')
    temp=target.with_suffix('.xapk.part')
    expected={}
    with ZipFile(source) as old:
        infos=old.infolist();names=[i.filename for i in infos]
        if len(names)!=4 or len(names)!=len(set(names)):raise ValueError('Unexpected original XAPK layout.')
        if any(n.startswith('/') or '..' in PurePosixPath(n).parts for n in names):raise ValueError('Unsafe archive path.')
        apks=[i for i in infos if i.filename.endswith('.apk')]
        obbs=[i for i in infos if i.filename.endswith('.obb')]
        if len(apks)!=1 or len(obbs)!=1 or 'manifest.json' not in names:raise ValueError('Expected one APK, one OBB and manifest.')
        apk=apks[0];obb=obbs[0]
        if apk.file_size!=APK_BYTES or sha(old.read(apk))!=ORIGINAL:raise ValueError('Original APK fingerprint mismatch.')
        if obb.filename!='Android/obb/com.tencent.tmgp.cfmnac/main.11.com.tencent.tmgp.cfmnac.obb' or obb.file_size!=OBB_BYTES:raise ValueError('Original OBB metadata mismatch.')
        if shutil.disk_usage(downloads).free < sum(i.file_size for i in infos)+len(payload)+64*1024*1024:raise ValueError('Not enough space for a separate XAPK.')
        if old.getinfo('manifest.json').file_size>65536:raise ValueError('Unexpected manifest size.')
        manifest=json.loads(old.read('manifest.json'))
        if not isinstance(manifest,dict):raise ValueError('Unsupported XAPK manifest object.')
        version=manifest.get('xapk_version',manifest.get('manifest_version'))
        if 'xapk_version' in manifest and 'manifest_version' in manifest and str(manifest['xapk_version'])!=str(manifest['manifest_version']):
            raise ValueError('Conflicting XAPK manifest versions.')
        if str(version) not in ('1','2') or manifest.get('package_name')!='com.tencent.tmgp.cfmnac':raise ValueError('Unsupported XAPK manifest schema or package.')
        original_apk=old.read(apk)
        replacements={}
        for algorithm in ('md5','sha1','sha256'):
            before=hashlib.new(algorithm,original_apk).hexdigest()
            after=hashlib.new(algorithm,payload).hexdigest()
            replacements[before]=after;replacements[before.upper()]=after.upper()
        def adjust(value,key=''):
            if isinstance(value,dict):return {k:adjust(v,k) for k,v in value.items()}
            if isinstance(value,list):return [adjust(v) for v in value]
            if key=='total_size':
                if isinstance(value,bool):raise ValueError('Invalid total_size.')
                n=int(value)+len(payload)-apk.file_size
                return str(n) if isinstance(value,str) else n
            if isinstance(value,str) and value in replacements:return replacements[value]
            if key in ('file_size','size','apk_size') and value in (apk.file_size,str(apk.file_size)):
                return str(len(payload)) if isinstance(value,str) else len(payload)
            return value
        manifest_bytes=(json.dumps(adjust(manifest),ensure_ascii=False,separators=(',',':'))+'\n').encode()
        print('Creating a separate XAPK; copying and checking the unchanged OBB...')
        with ZipFile(temp,'x') as new:
            for info in infos:
                clone=copy.copy(info)
                replacement=payload if info.filename==apk.filename else manifest_bytes if info.filename=='manifest.json' else None
                if replacement is not None:
                    new.writestr(clone,replacement);expected[info.filename]=sha(replacement)
                else:
                    digest=hashlib.sha256()
                    with old.open(info) as src,new.open(clone,'w') as dst:
                        while True:
                            block=src.read(1024*1024)
                            if not block:break
                            digest.update(block);dst.write(block)
                    expected[info.filename]=digest.hexdigest()
    print('Verifying every output payload...')
    with ZipFile(temp) as verify:
        if set(verify.namelist())!=set(expected):raise ValueError('Output entry mismatch.')
        for name,want in expected.items():
            digest=hashlib.sha256()
            with verify.open(name) as src:
                while True:
                    block=src.read(1024*1024)
                    if not block:break
                    digest.update(block)
            if digest.hexdigest()!=want:raise ValueError('Output verification failed.')
    temp.rename(target)
    report={'format':'CF2018_SIGNATURE_CONTROL_XAPK','control_apk_sha256':CONTROL,'original_apk_sha256':ORIGINAL,
            'all_output_payloads_verified':True,'obb_unchanged_sha256':expected[obb.filename],
            'xapk_file':target.name,'installation_performed':False,'android_runtime_tested':False}
    report_path=target.with_suffix('.txt')
    with report_path.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print('READY: '+str(target));print('Share report: '+str(report_path));print('Do not install yet.')
if __name__=='__main__':
    try:main()
    except Exception as error:
        print('STOPPED: '+str(error))
        raise SystemExit(1)
