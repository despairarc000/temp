"""Patch the exact private v38 ZIP locally. Preparation never starts a relay."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

SOURCE_SHA = 'e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2'
PREFIX = 'CF2018_TGCP_v3.8_GCloud_DataHead_Flags'
STARTER = '''#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -m unittest discover -s tests -p test_v38.py -q
if [ "${CF2018_V381_LIVE:-NO}" = YES ]; then
    python3 routed_probe_v38.py --live-opt-in
else
    echo 'Offline tests complete. No listener started.'
    echo 'Manual opt-in only: CF2018_V381_LIVE=YES bash START_V381.sh'
fi
'''


def patch_probe(original):
    marker = "        return {**profile,**compression_from_routed_frame(frame),"
    end = " rpc_verified=False auth_verified=False')"
    if original.count(marker) != 1 or original.count(end) != 1:
        raise ValueError('exact observer integration anchors required')
    patched = original.replace(marker, "        from routed_body_diagnostic import inspect_v38_frame\n" +
                               "        return {**inspect_v38_frame(frame),**profile,**compression_from_routed_frame(frame),")
    extra = (' sequence_prefix={e.get("sequence_prefix","NOT_COMPARABLE")}'
             ' legacy_at_start={e.get("legacy_at_start","NOT_COMPARABLE")}'
             ' legacy_after_sequence={e.get("legacy_after_sequence","NOT_COMPARABLE")}'
             ' known_address_route={e.get("known_address_route","UNKNOWN")}')
    patched = patched.replace(end, extra + end)
    patched = patched.replace('CF2018 v3.8', 'CF2018 v3.8.1 Sequence Boundary')
    patched = patched.replace('CF2018_V37_LIVE=YES', 'CF2018_V381_LIVE=YES bash START_V381.sh')
    patched = patched.replace('cf2018_v38_runs', 'cf2018_v381_runs')
    patched = patched.replace('CF2018_v38_DataHead_Result.txt', 'CF2018_v381_Sequence_Boundary_Result.txt')
    patched = patched.replace("f'Completed sessions:", "f'RUN_ID={run.run_id}',\n         f'Completed sessions:")
    patched = patched.replace('}: local_port={accepted.get', '}: cid={x["cid"]} local_port={accepted.get')
    patched = patched.replace('DISCLAIMERS: all packets are synthetic; WAIT and Bingo do not create real accounts/sessions.',
                              'DISCLAIMERS: server replies are synthetic; client traffic is not authentication proof.')
    compile(patched, 'routed_probe_v38.py', 'exec')
    return patched


def prepare(archive, output, bundle=None):
    archive, output = Path(archive).resolve(), Path(output).resolve()
    bundle = Path(bundle or Path(__file__).parent).resolve()
    if output.exists():
        raise ValueError('new output folder required; original folder never overwritten')
    if archive.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('unexpected source ZIP size')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('requires the exact original v38 ZIP; hash mismatch')
    pins = json.loads((bundle / 'V38_SOURCE_PINS.json').read_text())
    payloads = {}
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist()) != len(pins):
            raise ValueError('unexpected archive entry count')
        for entry in z.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or '..' in path.parts or path.parts[0] != PREFIX:
                raise ValueError('unsafe source entry')
            name = path.relative_to(PREFIX).as_posix()
            if name in payloads or name not in pins or entry.file_size > 262144:
                raise ValueError('unexpected source entry')
            data = z.read(entry)
            if hashlib.sha256(data).hexdigest() != pins[name]:
                raise ValueError('source entry hash mismatch')
            payloads[name] = data
    payloads['routed_probe_v38.py'] = patch_probe(payloads['routed_probe_v38.py'].decode()).encode()
    relay = payloads['cf2018_redirector.py'].decode()
    old = "return port in TARGET_PORTS and (host.lower().rstrip('.') in TARGET_DOMAINS or host in TARGET_IPS)"
    if relay.count(old) != 1:
        raise ValueError('exact routing anchor required')
    # Keep non-target normal passthrough; only divert exact known IP+port pairs.
    relay = relay.replace(old, 'return port in TARGET_PORTS and host in TARGET_IPS')
    payloads['cf2018_redirector.py'] = relay.encode()
    payloads['routed_body_diagnostic.py'] = (bundle / 'routed_body_diagnostic.py').read_bytes()
    payloads['START_V381.sh'] = STARTER.encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.cf18_prepare_', dir=output.parent) as temp:
        root = Path(temp) / 'prepared'
        root.mkdir()
        for name, data in payloads.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        root.rename(output)
    return {'prepared': True, 'relay_started': False, 'stage_bytes_changed': False,
            'routing': 'EXACT_KNOWN_IP_AND_PORT_ONLY',
            'report': 'CF2018_v381_Sequence_Boundary_Result.txt'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.zip, args.output), sort_keys=True))
