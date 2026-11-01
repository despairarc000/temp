"""Offline-only R037 dispatch integration; requires exact supplied ZIP + V3.8.

Preserves R037 live opt-in and one address-reply maximum. Never auto-ACKs
the second route, runs a listener, or modifies the game or input sources.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
from prepare_second_service_dispatch import ROOT, INSERT, REPORT_ANCHOR, REPORT_INSERT, MODULES

KIT_SHA = 'c9837375ed0d5b37606e9619d1597c544d60de8d2684c3e8ea6eb657378fc380'
PROBE_SHA = '2c28c09944770a66ffca7c7bdf19dd6065fce7ea59766b98bf58e5078e2e2e01'
GATE = "                        if frame['sha256'] != expected or sel != [[0x1001, 5]]:\n"
CONTEXT_INSERT = (
    '                        from second_service_syn_gate import compare_security_context\n'
    "                        assessment = 'REFERENCE_EXACT' if raw_frame == original else compare_security_context(raw_frame, original)\n"
    "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment)\n"
)
CONTEXT_REPORT = (
    '    for e in ev:\n'
    "        if e['action'] == 'syn_security_context':\n"
    "            out.append(f\"SYN_CONTEXT slot={e['slot']} class={e['assessment']}\")\n"
)


def patch_probe(text):
    if hashlib.sha256(text.encode()).hexdigest() != PROBE_SHA:
        raise ValueError('exact generated R037 handler required')
    if text.count(GATE) != 1 or text.count(REPORT_ANCHOR) != 1:
        raise ValueError('R037 integration anchor changed')
    patched = text.replace(GATE, CONTEXT_INSERT + INSERT + GATE).replace(
        REPORT_ANCHOR, CONTEXT_REPORT + REPORT_INSERT + REPORT_ANCHOR)
    assert patched.replace(CONTEXT_INSERT, '', 1).replace(INSERT, '', 1).replace(
        CONTEXT_REPORT, '', 1).replace(REPORT_INSERT, '', 1) == text
    compile(patched, 'routed_probe_r037.py', 'exec')
    return patched


def prepare(source, kit, output):
    source, kit, output = map(lambda p: Path(p).resolve(), (source, kit, output))
    if output.exists() or source == output or source in output.parents:
        raise ValueError('fresh output outside source required')
    if not output.is_relative_to(ROOT / 'private'):
        raise ValueError('private output required')
    if kit.stat().st_size != 35193 or hashlib.sha256(kit.read_bytes()).hexdigest() != KIT_SHA:
        raise ValueError('R037 attachment fingerprint mismatch')
    # Pinning bounds all ZIP contents before executing its source preparer.
    (ROOT / 'private').mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / 'private') as tmp:
        with zipfile.ZipFile(kit) as z:
            for n in z.namelist():
                if Path(n).is_absolute() or '..' in Path(n).parts:
                    raise ValueError('unsafe archive path')
            if z.testzip() is not None:
                raise ValueError('archive integrity failure')
            z.extractall(tmp)
        root = Path(tmp) / 'CF2018_R037_ROUTE_DELTA_Kit'
        generated = root / 'private' / 'generated'
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        subprocess.run([sys.executable, str(root / 'tools/prepare_r037.py'),
                        '--source', str(source), '--output', str(generated)],
                       check=True, capture_output=True, text=True, timeout=60, env=env)
        original = (generated / 'routed_probe_r037.py').read_text()
        patched = patch_probe(original)
        modules = {n: (ROOT / 'experiments' / n).read_bytes()
                   for n in (*MODULES, 'second_service_syn_gate.py')}
        shutil.copytree(generated, output)
        (output / 'routed_probe_r037.py').write_text(patched)
        for n, data in modules.items():
            (output / n).write_bytes(data)
    return {'prepared': True, 'attachment_verified': True,
            'r037_handler_verified': True, 'address_reply_changes': False,
            'second_service_ack_enabled': False, 'listener_started': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--kit', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.source, a.kit, a.output), sort_keys=True))
