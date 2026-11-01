"""Prepare a separately opted-in one-ACK experiment, never start a listener."""
import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from prepare_r037_dispatch import prepare as prepare_dispatch, ROOT


def patch_probe(text):
    from prepare_r037_dispatch import INSERT, REPORT_ANCHOR
    old_gate = "                        if frame['sha256'] != expected or sel != [[0x1001, 5]]:\n"
    start = '        started=time.monotonic(); after_auth_ms=None;auth_sent_time=None\n'
    ack_record = "                        run.record('ack_sent',cid,slot=slot,reply_bytes=sent_ack)\n"
    follow = '                    elif frames==2:\n'
    if hashlib.sha256(text.encode()).hexdigest() != 'e9a255661f37ddf85e0d8c02949bafc0c399ce36819e6e60ccf1370ce92ed64e':
        raise ValueError('exact verified context handler required')
    # Only a verified dispatch copy produced by the exact preparer is accepted.
    if text.count(INSERT) != 1 or text.count('syn_security_context') != 2:
        raise ValueError('verified R037 context instrumentation required')
    replacements = {
        "Path.home()/'cf2018_r037_runs'/": "Path.home()/'cf2018_second_service_ack_runs'/",
        "Path.home()/'storage/downloads/CF2018_R037_ROUTE_Result.txt'": "Path.home()/'storage/downloads/CF2018_SECOND_SERVICE_ACK_Result.txt'",
        "out=['CF2018 v3.8 — GCloud DataHead compression flag and legacy-Thrift control; same four synthetic Bingo trials',": "out=['CF2018 second-service one-ACK experiment; not an authenticated session',",
        start: start + '        second_service_probe=False\n',
        INSERT: """                        from r056_second_service_syn import first_syn_decision
                        route_class, disposition = first_syn_decision(raw_frame)
                        if (assessment == 'MATCH_EXCEPT_ROUTE' and
                            __import__('os').environ.get('CF2018_SECOND_SERVICE_ACK') == 'YES'):
                            with run.lock:
                                if (run.r033_reply_sent_at is not None and
                                    not getattr(run,'second_service_ack_claimed',False)):
                                    run.second_service_ack_claimed=True
                                    second_service_probe=True
                                    disposition='ONE_SHOT_ACK_PROBE'
                        run.record('first_syn_dispatch',cid,slot=slot,classification=route_class,disposition=disposition)
                        if disposition != 'DEFER_TO_PINNED_REFERENCE_GATE' and not second_service_probe:
                            status='next_route_held_no_ack';break
""",
        old_gate: "                        if not second_service_probe and (frame['sha256'] != expected or sel != [[0x1001, 5]]):\n",
        ack_record: ack_record + """                        if second_service_probe:
                            run.record('second_service_ack_written',cid,slot=slot,status='ACK_WRITTEN')
""",
        follow: follow + """                        if second_service_probe:
                            status=('AUTH_REQUEST_OBSERVED' if sel == [[0x2001,1]] else 'OTHER_FRAME_OBSERVED')
                            run.record('second_service_followup',cid,slot=slot,status=status)
                            break
""",
        REPORT_ANCHOR: """    for e in ev:
        if e['action'] in ('second_service_ack_written','second_service_followup'):
            out.append(f"SECOND_SERVICE slot={e['slot']} status={e['status']}")
""" + REPORT_ANCHOR,
    }
    patched = text
    for old, new in replacements.items():
        if patched.count(old) != 1:
            raise ValueError('exact instrumentation anchor changed')
        patched = patched.replace(old, new)
    recovered = patched
    for old, new in reversed(list(replacements.items())):
        recovered = recovered.replace(new, old, 1)
    if recovered != text:
        raise ValueError('unexpected non-instrumentation edit')
    compile(patched, 'routed_probe_r037.py', 'exec')
    return patched


def prepare(source, kit, output):
    result = prepare_dispatch(source, kit, output)
    dest = Path(output).resolve()
    p = dest / 'routed_probe_r037.py'
    p.write_text(patch_probe(p.read_text()))
    shutil.copyfile(ROOT / 'tests/test_second_service_ack_lifecycle.py', dest / 'test_second_service_ack_lifecycle.py')
    (dest / 'START_SECOND_SERVICE_ACK.sh').write_text('''#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
env -u CF2018_SECOND_SERVICE_ACK -u CF2018_R037_LIVE_REPLY python3 -m unittest discover -s tests -q
CF18_R037_PREPARED="$PWD" python3 -m unittest -q test_second_service_ack_lifecycle
if [ "${CF2018_SECOND_SERVICE_ACK:-NO}" = YES ] && [ "${CF2018_R037_LIVE_REPLY:-NO}" = YES ]; then
  python3 routed_probe_r037.py --live-opt-in
else
  echo 'Offline tests passed. No phone listener started. Both explicit live opt-ins are required.'
fi
''')
    return {**result, 'one_ack_experiment_prepared': True,
            'second_service_ack_enabled': False, 'listener_started': False}


def prepare_from_zip(source_zip, kit, output):
    source_zip = Path(source_zip).resolve()
    if hashlib.sha256(source_zip.read_bytes()).hexdigest() != 'e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2':
        raise ValueError('exact original V3.8 source ZIP required')
    (ROOT / 'private').mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / 'private') as tmp:
        with zipfile.ZipFile(source_zip) as z:
            if z.testzip() is not None:
                raise ValueError('source ZIP integrity failure')
            for n in z.namelist():
                if Path(n).is_absolute() or '..' in Path(n).parts:
                    raise ValueError('unsafe source path')
            z.extractall(tmp)
        handlers = list(Path(tmp).rglob('routed_probe_v38.py'))
        if len(handlers) != 1:
            raise ValueError('unique original handler required')
        return prepare(handlers[0].parent, kit, output)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--source')
    source.add_argument('--source-zip')
    for name in ('kit', 'output'):
        p.add_argument('--' + name, required=True)
    a = p.parse_args()
    fn = prepare_from_zip if a.source_zip else prepare
    print(json.dumps(fn(a.source_zip or a.source, a.kit, a.output), sort_keys=True))
