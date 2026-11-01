"""Read-only extractor for original CF2018 Unity Managed DLL from local XAPK.

Does not modify XAPK, install/repack an APK, or contact the network.
Requires original DLL hash before creating final output. Keep binary private.
"""
from pathlib import Path
import argparse,hashlib,os,shutil,tempfile,zipfile
INNER_APK='com.tencent.tmgp.cfmnac.apk'
INNER_DLL='assets/bin/Data/Managed/Assembly-CSharp.dll'
ORIGINAL_DLL_SHA256='174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9'
MAX_ASSEMBLY_BYTES=100_000_000

def extract(source:Path,destination:Path,expected_sha256:str=ORIGINAL_DLL_SHA256):
    """On failure never leave wrong-hash output; refuse overwriting any file."""
    source=Path(source);destination=Path(destination)
    if not source.is_file():raise FileNotFoundError('original XAPK unavailable')
    if destination.exists():raise FileExistsError('destination exists: refusing overwrite')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cf18-private-apk-') as tmp:
        apk_temp=Path(tmp)/'original_app.apk'
        with zipfile.ZipFile(source,'r') as outer:
            with outer.open(INNER_APK,'r') as src,apk_temp.open('wb') as out:
                shutil.copyfileobj(src,out,1024*1024)
        with zipfile.ZipFile(apk_temp,'r') as apk:
            entry=apk.getinfo(INNER_DLL)
            if entry.file_size<1 or entry.file_size>MAX_ASSEMBLY_BYTES:
                raise ValueError('assembly exceeds permitted byte-size limit')
            tmpout=destination.parent/(destination.name+'.incomplete')
            if tmpout.exists():raise FileExistsError('incomplete temp output exists')
            h=hashlib.sha256();total=0
            try:
                with apk.open(entry,'r') as src,tmpout.open('xb') as dst:
                    while True:
                        block=src.read(1024*1024)
                        if not block:break
                        total+=len(block)
                        if total>MAX_ASSEMBLY_BYTES:raise ValueError('assembly too large')
                        h.update(block);dst.write(block)
                if total!=entry.file_size or h.hexdigest()!=expected_sha256:
                    raise ValueError('original DLL SHA256 mismatch: refusing altered assembly')
                os.replace(tmpout,destination)
            finally:
                if tmpout.exists():tmpout.unlink()
    return {'verified':True,'bytes':total,'sha256':h.hexdigest(),
        'output':str(destination),'original_xapk_unchanged':True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--xapk',default=str(Path.home()/'storage/downloads/Original.xapk'))
    p.add_argument('--output',default=str(Path.home()/'cf2018_original_private/Assembly-CSharp.dll'))
    args=p.parse_args()
    try:r=extract(Path(args.xapk),Path(args.output))
    except (OSError,ValueError,zipfile.BadZipFile,KeyError) as e:
        print('REFUSED:',type(e).__name__,str(e));raise SystemExit(2)
    print('VERIFIED ORIGINAL DLL')
    print('Bytes:',r['bytes'])
    print('SHA256:',r['sha256'])
    print('Saved:',r['output'])
    print('Never publish original DLL in GitHub or source-only test kits.')
if __name__=='__main__':main()
