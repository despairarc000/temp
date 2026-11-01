"""Standalone copy-only diagnostic patch. No listeners start on preparation."""
import argparse
import hashlib
import inspect
from pathlib import Path
import shutil


def diagnose(candidate, reference):
    from second_service_syn_gate import _parts, compare_security_context
    from r056_second_service_syn import first_syn_decision
    fallback = dict(reason='NOT_COMPARABLE', base_changed=[], syn_changed=[])
    try:
        if type(candidate) is not bytes or type(reference) is not bytes:
            return fallback
        if len(reference) != 133 or len(candidate) not in (131, 133):
            return fallback
        if first_syn_decision(reference)[0] != 'REFERENCE_NAMED_ROUTE_CANDIDATE':
            return fallback
        if candidate == reference:
            return dict(reason='REFERENCE_EXACT', base_changed=[], syn_changed=[])
        if first_syn_decision(candidate)[0] != 'TEN_BYTE_NAMED_ROUTE_CANDIDATE':
            return fallback
        a, _, sa, _, _ = _parts(reference)
        b, _, sb, _, _ = _parts(candidate)
        from second_service_syn_gate import _records
        def changed(x, y, omit=None):
            left = {f[0]: f for f in x}; right = {f[0]: f for f in y}
            return [[n, right[n][1] if n in right else left[n][1]]
                    for n in sorted(left.keys() | right.keys())
                    if n != omit and (n not in left or n not in right or left[n][3] != right[n][3])]
        base = changed(_records(a[0][2]), _records(b[0][2]))
        syn = changed(sa, sb, 14)
        reason = ('BASE_FIELDS_CHANGED' if base else 'NON_ROUTE_SYN_CHANGED' if syn else
                  'MATCH_EXCEPT_ROUTE' if compare_security_context(candidate, reference) == 'MATCH_EXCEPT_ROUTE'
                  else 'ENCODING_OR_SHAPE_DIFFERENCE')
        return dict(reason=reason, base_changed=base, syn_changed=syn)
    except (ValueError, TypeError, IndexError, StopIteration, OverflowError):
        return fallback


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists() or source == output or source in output.parents:
        raise ValueError('fresh output outside source required')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('symlinks refused')
    handler = source / 'routed_probe_r037.py'
    text = handler.read_text()
    expected = '7ab7ad90735201b6df96265c8dd379d08308690fb6956f3a46e4f793ba8c84d0'
    if hashlib.sha256(text.encode()).hexdigest() != expected:
        raise ValueError('exact one-ACK experiment handler required')
    if hashlib.sha256((source / 'second_service_syn_gate.py').read_bytes()).hexdigest() != '9f7ee1969541ca27a1da48a4f91d4edab89d726383c71513efbe6e357072a43e':
        raise ValueError('gate source mismatch')
    old = "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment)\n"
    new = ("                        from syn_difference_labels import diagnose\n"
           "                        run.record('syn_security_context',cid,slot=slot,assessment=assessment,**diagnose(raw_frame,original))\n")
    changes = {
        old: new,
        "__import__('os').environ.get('CF2018_SECOND_SERVICE_ACK') == 'YES'": 'False',
        "class={e['assessment']}\")": "class={e['assessment']} reason={e['reason']} base_changed={e['base_changed']} syn_changed={e['syn_changed']}\")",
        'CF2018_SECOND_SERVICE_ACK_Result.txt': 'CF2018_SYN_DIFFERENCE_Result.txt',
        'cf2018_second_service_ack_runs': 'cf2018_syn_difference_runs',
        'CF2018 second-service one-ACK experiment; not an authenticated session': 'CF2018 SYN difference diagnostic; second-service ACK disabled',
    }
    for old, new in changes.items():
        if text.count(old) != 1:
            raise ValueError('exact diagnostic anchor changed')
        text = text.replace(old, new)
    compile(text, str(handler), 'exec')
    helper = inspect.getsource(diagnose)
    compile(helper, 'syn_difference_labels.py', 'exec')
    shutil.copytree(source, output, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (output / handler.name).write_text(text)
    (output / 'syn_difference_labels.py').write_text(helper)
    return {'prepared': True, 'second_service_ack_disabled': True, 'listener_started': False}


if __name__ == '__main__':
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True); p.add_argument('--output', required=True)
    args = p.parse_args()
    print(json.dumps(prepare(args.source, args.output), sort_keys=True))
