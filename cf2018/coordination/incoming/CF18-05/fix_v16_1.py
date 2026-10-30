"""Safely upgrade the existing CF2018 v1.6 observer to v1.6.1.

Requires exact original v1.6 SHA256 pins. Modifies only two generated observer
files; v1.5 handshake, server messages, client assets and private fixtures are
untouched. No network traffic or phone run.
"""
from hashlib import sha256
from pathlib import Path
import ast
import sys

BASE = Path(__file__).resolve().parent
UPDATED = {
    'route_probe_v16.py': '8270595a913c2386acc3d19f07840934aa48a2ffc46fe64be03227018db84c5b',
    'route_fingerprint_v16.py': 'f6b75383ec5d078c25b676aaec716ca588464a5518c14b0c45d8a9e4194a0aeb',
}
EXPECTED = {
    'route_probe_v16.py': '054ded025008667df931c34495f29999b1805d12529250057caf9e91a5e1fbb2',
    'route_fingerprint_v16.py': '9ce0b797ef06aa60d1f725fca4e60cf534ed273523a39567c65b677ef14ab1c8',
}


def replace_once(code, old, new):
    if code.count(old) != 1:
        raise ValueError('exact v1.6 patch anchor is missing or repeated; no changes made: '+old[:80])
    return code.replace(old, new)


def main():
    raw = {}
    hashes = {name:sha256((BASE/name).read_bytes()).hexdigest() for name in EXPECTED}
    if hashes == UPDATED:
        print('v1.6.1 already installed. No changes needed.')
        return
    for name, digest in EXPECTED.items():
        src = (BASE / name).read_bytes()
        actual = sha256(src).hexdigest()
        if actual != digest:
            raise ValueError(name+' SHA256 mismatch; no files modified. Observed '+actual)
        raw[name] = src.decode('utf-8')

    fp = replace_once(raw['route_fingerprint_v16.py'],
        "    if structure.get('extension_fields') != [[0x4013, 1]]:\n        raise ValueError('only exact 0x4013 routed client frames supported')",
        "    selectors = structure.get('extension_fields')\n"
        "    if (not isinstance(selectors, list) or len(selectors) != 1\n"
        "            or not isinstance(selectors[0], list) or len(selectors[0]) != 2\n"
        "            or selectors[0][0] != 0x4013 or selectors[0][1] not in (1, 5)):\n"
        "        raise ValueError('unsupported routed selector type or wire kind')")
    fp = replace_once(fp,
        "    return {'route_type': '0x4013', 'frame_bytes': len(frame),",
        "    return {'route_type': '0x4013', 'selector_kind': selectors[0][1],\n"
        "            'frame_bytes': len(frame),")
    obs = replace_once(raw['route_probe_v16.py'],
        "                        if sel == [[0x4013,1]]:\n                            run.record('routed_rpc_hint',cid,slot=slot,**inspect_routed_frame(wire_frame,frame))",
        "                        if kind == 0x4013:\n"
        "                            try:\n"
        "                                hint=inspect_routed_frame(wire_frame,frame)\n"
        "                            except (ValueError,TypeError):\n"
        "                                # Always log a classification result, even for unknown\n"
        "                                # selector shapes or unsupported frame metadata.\n"
        "                                # Never save input bytes, token or arbitrary strings.\n"
        "                                hint={'route_type':'0x4013',\n"
        "                                      'selector_kind':sel[0][1] if len(sel)==1 else None,\n"
        "                                      'frame_bytes':frame['frame_bytes'],\n"
        "                                      'header_bytes':frame['header_bytes'],\n"
        "                                      'body_bytes':frame['body_bytes'],\n"
        "                                      'body_envelope_hint':'NOT_INSPECTED',\n"
        "                                      'rpc_hint':'INSPECTION_REJECTED',\n"
        "                                      'rpc_offset':None,\n"
        "                                      'rpc_type_hint':'UNKNOWN',\n"
        "                                      'rpc_confidence':'UNSUPPORTED_FRAME_OR_SELECTOR'}\n"
        "                            run.record('routed_rpc_hint',cid,slot=slot,**hint)")
    obs = replace_once(obs,
        "out.append('ROUTED_HINT slot={} type={} frame={} header={} body={} envelope={} method={} offset={} rpc_type={} confidence={}'.format(\n            h['slot'],h['route_type'],h['frame_bytes'],h['header_bytes'],h['body_bytes'],",
        "out.append('ROUTED_HINT slot={} type={} kind={} frame={} header={} body={} envelope={} method={} offset={} rpc_type={} confidence={}'.format(\n            h['slot'],h['route_type'],h['selector_kind'],h['frame_bytes'],h['header_bytes'],h['body_bytes'],")
    obs = replace_once(obs,
        "'CF2018 v1.6 — post-Bingo 0x4013 privacy-safe RPC fingerprint'",
        "'CF2018 v1.6.1 — selector-kind-aware post-Bingo 0x4013 RPC fingerprint'")
    obs = replace_once(obs,
        'CF2018_v16_Routed_Fingerprint_Result.txt',
        'CF2018_v161_Routed_Fingerprint_Result.txt')
    for n,s in [('route_fingerprint_v16.py',fp),('route_probe_v16.py',obs)]:
        ast.parse(s,n)
    # Finish validation for every input BEFORE updating either file.
    for n,s in [('route_fingerprint_v16.py',fp),('route_probe_v16.py',obs)]:
        (BASE/n).write_text(s,encoding='utf-8')
        print(n,sha256(s.encode('utf-8')).hexdigest())
    print('v1.6.1 installed. START_V16.sh / original v1.5 remain unchanged.')

if __name__ == '__main__':
    try: main()
    except (ValueError,FileNotFoundError,UnicodeDecodeError) as exc:
        print('Upgrade not applied:',exc,file=sys.stderr)
        raise SystemExit(1)
