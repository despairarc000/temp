"""Prepare a private COPY with fixed-label diagnostics; never start the relay.

Requires the exact supplied v38 source. Existing startup opt-in, session limits,
ports, endpoint routing and all synthetic replies remain unchanged.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists() or source == output or source in output.parents:
        raise ValueError('new output outside original source required')
    if not output.is_relative_to(ROOT / 'private'):
        raise ValueError('private workspace output required')
    pins = json.loads((ROOT / 'coordination/V38_SOURCE_PINS.json').read_text())
    for name, expected in pins.items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError('source mismatch: ' + name)
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('symlink source refused')
    original = (source / 'routed_probe_v38.py').read_text()
    marker = "        return {**profile,**compression_from_routed_frame(frame),"
    end = " rpc_verified=False auth_verified=False')"
    if original.count(marker) != 1 or original.count(end) != 1:
        raise ValueError('exact integration anchors required')
    patched = original.replace(marker, "        from routed_body_diagnostic import inspect_v38_frame\n" +
                               "        return {**inspect_v38_frame(frame),**profile,**compression_from_routed_frame(frame),")
    extra = (' sequence_prefix={e.get("sequence_prefix","NOT_COMPARABLE")}'
             ' legacy_at_start={e.get("legacy_at_start","NOT_COMPARABLE")}'
             ' legacy_after_sequence={e.get("legacy_after_sequence","NOT_COMPARABLE")}'
             ' known_address_route={e.get("known_address_route","UNKNOWN")}')
    patched = patched.replace(end, extra + end)
    compile(patched, 'routed_probe_v38.py', 'exec')
    shutil.copytree(source, output, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (output / 'routed_probe_v38.py').write_text(patched)
    shutil.copyfile(ROOT / 'experiments/routed_body_diagnostic.py', output / 'routed_body_diagnostic.py')
    return {'prepared': True, 'relay_started': False, 'wire_changes': False,
            'diagnostic_fields': ['sequence_prefix', 'legacy_at_start',
                                  'legacy_after_sequence', 'known_address_route']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.source, a.output), sort_keys=True))
