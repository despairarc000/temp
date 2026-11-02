"""Locate one configuration reference in the exact original APK, read-only.

Requires optional UnityPy. Returns resource-index metadata only; no original
object content, scripts, images, account values or extracted files are written.
"""
import hashlib,re
from pathlib import Path
from zipfile import ZipFile
APK_SHA='33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9'
RESOURCE='config/system/gcloudsetting_'

def locate(apk):
    path=Path(apk)
    if path.stat().st_size!=30884905 or hashlib.sha256(path.read_bytes()).hexdigest()!=APK_SHA:
        raise ValueError('exact original APK required')
    import UnityPy
    with ZipFile(path) as archive:
        data=archive.read('assets/bin/Data/mainData')
    env=UnityPy.load(data);matches=[]
    for obj in env.objects:
        if obj.type.name!='ResourceManager':continue
        entries=list(obj.read().m_Container)
        for name,pointer in entries:
            if name!=RESOURCE:continue
            fileid=pointer.m_FileID
            if not 1<=fileid<=len(obj.assets_file.externals):
                raise ValueError('external resource index invalid')
            external=obj.assets_file.externals[fileid-1].path
            if not re.fullmatch('[a-f0-9]{32}',external):
                raise ValueError('unexpected resource filename form')
            matches.append({'resource':RESOURCE,'file_id':fileid,'path_id':pointer.m_PathID,
                            'external_file':external,'index_entries':len(entries),
                            'main_data_sha256':hashlib.sha256(data).hexdigest()})
    if len(matches)!=1:raise ValueError('expected exactly one resource reference')
    return matches[0]
