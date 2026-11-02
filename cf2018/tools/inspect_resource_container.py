"""Read-only asset-container labels and one exact configuration-entry lookup.

No game launch, socket, game-file edit, raw header/content export or extraction.
Only a small text report is written. Handles a renamed ZIP without trusting its
extension; bounds central-directory metadata before opening it.
"""
import argparse,json,struct,zipfile
from pathlib import Path
TARGET='7346236864af94314bae0701e3cddcd2'
MAX_INDEX=8*1024*1024

def inspect(path):
    path=Path(path);size=path.stat().st_size
    if not path.is_file() or size<1:raise ValueError('nonempty regular source file required')
    with path.open('rb') as stream:
        head=stream.read(32)
        stream.seek(max(0,size-65557));tail=stream.read(65557)
    signature='UNKNOWN'
    for magic,label in ((b'\x89PNG\r\n\x1a\n','PNG'),(b'PK\x03\x04','ZIP'),
                        (b'UnityFS\0','UNITYFS'),(b'UnityRaw\0','UNITYRAW'),
                        (b'UnityWeb\0','UNITYWEB'),(b'UnityArchive\0','UNITYARCHIVE')):
        if head.startswith(magic):signature=label;break
    result={'source_bytes':size,'expected_drive_size_match':size==431231509,'header_kind':signature,
            'zip_index':'NOT_IDENTIFIED','configuration_entry':'UNKNOWN'}
    end=tail.rfind(b'PK\x05\x06')
    if end<0 or len(tail)-end<22:return result
    record=struct.unpack_from('<4s4H2LH',tail,end)
    _,disk,cd_disk,count_disk,count,cd_size,cd_offset,comment=record
    if end+22+comment!=len(tail):
        result['zip_index']='END_RECORD_INCONSISTENT';return result
    if disk or cd_disk or count_disk!=count:
        result['zip_index']='MULTIPART_UNSUPPORTED';return result
    if count==65535 or cd_size==0xffffffff or cd_offset==0xffffffff:
        result['zip_index']='ZIP64_UNSUPPORTED';return result
    if count>16384 or cd_size>MAX_INDEX or cd_size>size:
        result['zip_index']='METADATA_BOUND_EXCEEDED';return result
    try:
        with zipfile.ZipFile(path) as archive:
            entries=archive.infolist()
            if len(entries)!=count:raise ValueError('index count mismatch')
            matches=[e for e in entries if e.filename.replace('\\','/').rsplit('/',1)[-1]==TARGET]
            result.update(zip_index='PARSED',zip_entries=len(entries),
                          configuration_entry='PRESENT' if matches else 'NOT_IN_THIS_ZIP',
                          configuration_matches=len(matches))
            if len(matches)==1:
                entry=matches[0]
                result.update(configuration_bytes=entry.file_size,
                              configuration_compressed_bytes=entry.compress_size,
                              configuration_encrypted=bool(entry.flag_bits&1))
    except (OSError,ValueError,zipfile.BadZipFile):
        result['zip_index']='INVALID_INDEX'
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',default=str(Path.home()/'storage/downloads/Assets.png'))
    parser.add_argument('--output',default=str(Path.home()/'storage/downloads/CF2018_RESOURCE_CONTAINER_Result.txt'))
    args=parser.parse_args();source=Path(args.source).resolve();output=Path(args.output).resolve()
    if source==output or output.is_symlink() or (output.exists() and source.samefile(output)):
        raise ValueError('report must not replace or alias original source')
    result=inspect(source)
    report='CF2018 read-only source-container inspection; not a phone/gameplay test\n'+json.dumps(result,sort_keys=True,indent=2)+'\nNo source contents, paths, URLs, credentials or raw bytes exported.\n'
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(report)
    print(report);print('Report:',output)

if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as exc:raise SystemExit(str(exc))
