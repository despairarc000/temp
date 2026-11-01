"""Prepare separate private observer copy; no live traffic or outgoing changes.

Requires exact pinned V3.8 source. Reuses previous validated observer-copy
preparation and adds one fixed-label qualified address request classification.
"""
import argparse
import json
import shutil
from pathlib import Path
from prepare_v38_observer import ROOT, prepare as prepare_base

def prepare(source,output):
    result=prepare_base(source,output)
    dest=Path(output).resolve()
    probe=dest/'routed_probe_v38.py'
    content=probe.read_text()
    anchor='        return {**inspect_v38_frame(frame),**profile,**compression_from_routed_frame(frame),'
    replacement=('        from qualified_frame_inspector import inspect_qualified_frame\n'
                 '        return {**inspect_v38_frame(frame),**inspect_qualified_frame(frame),'
                 '**profile,**compression_from_routed_frame(frame),')
    report_end=" rpc_verified=False auth_verified=False')"
    if content.count(anchor)!=1 or content.count(report_end)!=1:
        raise ValueError('base observer anchors changed')
    content=content.replace(anchor,replacement)
    content=content.replace(report_end,
       ' qualified_address_request={e.get("qualified_address_request","NOT_COMPARABLE")}'
       +report_end)
    compile(content,str(probe),'exec')
    for name in ('qualified_address_request.py','qualified_frame_inspector.py'):
        shutil.copyfile(ROOT/'experiments'/name,dest/name)
    probe.write_text(content)
    return {**result,'qualified_label_added':True,
            'outgoing_stage_changed':False,'request_bytes_written_to_report':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    print(json.dumps(prepare(args.source,args.output),sort_keys=True))
