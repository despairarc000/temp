"""Copy-only integration of R056 into the exact private V3.8 baseline.

Does not start a listener, authorize a new ACK, or replace the R037 reply kit.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER_SHA = 'ea3b6d79bfcbdaadcca8d8cff2305512394f58135f9277e8f05aa3fbf8200ff0'
ANCHOR = '                    if frames==1:\n'
INSERT = (
    '                        from r056_second_service_syn import first_syn_decision\n'
    '                        route_class, disposition = first_syn_decision(raw_frame)\n'
    "                        run.record('first_syn_dispatch',cid,slot=slot,classification=route_class,disposition=disposition)\n"
    "                        if disposition != 'DEFER_TO_PINNED_REFERENCE_GATE':\n"
    "                            status='next_route_held_no_ack';break\n"
)
MODULES = ('r056_second_service_syn.py', 'rx_envelope.py',
           'inbound_4013_reply_preflight.py', 'address_response_gate.py')
REPORT_ANCHOR = "    out+=['','DISCLAIMERS:"
REPORT_INSERT = (
    "    for e in ev:\n"
    "        if e['action'] == 'first_syn_dispatch':\n"
    "            out.append(f\"FIRST_SYN slot={e['slot']} class={e['classification']} disposition={e['disposition']}\")\n"
)


def patch_source(text):
    if hashlib.sha256(text.encode()).hexdigest() != HANDLER_SHA:
        raise ValueError('exact baseline handler required; R037/current deployed copies are not interchangeable')
    if text.count(ANCHOR) != 1 or text.count(REPORT_ANCHOR) != 1:
        raise ValueError('dispatch anchor changed')
    patched = text.replace(ANCHOR, ANCHOR + INSERT)
    patched = patched.replace(REPORT_ANCHOR, REPORT_INSERT + REPORT_ANCHOR)
    # Removing the insertion must recover every original character.
    assert patched.replace(INSERT, '', 1).replace(REPORT_INSERT, '', 1) == text
    compile(patched, 'routed_probe_v38.py', 'exec')
    return patched


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists() or source == output or source in output.parents:
        raise ValueError('fresh output outside input required')
    if not output.is_relative_to(ROOT / 'private'):
        raise ValueError('private workspace output required')
    pins = json.loads((ROOT / 'coordination/V38_SOURCE_PINS.json').read_text())
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('symlink source refused')
    for name, expected in pins.items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError('source mismatch: ' + name)
    patched = patch_source((source / 'routed_probe_v38.py').read_text())
    # Read every dependency before creating output; preserve existing replies,
    # limits, redirector, live opt-in and report exporter byte for byte.
    modules = {name: (ROOT / 'experiments' / name).read_bytes() for name in MODULES}
    output.mkdir(parents=True)
    for name in pins:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    (output / 'routed_probe_v38.py').write_text(patched)
    for name, data in modules.items():
        (output / name).write_bytes(data)
    return {'prepared': True, 'listener_started': False,
            'unknown_route_ack': False, 'baseline_source_files_verified': len(pins),
            'r037_reply_integration': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.source, a.output), sort_keys=True))
