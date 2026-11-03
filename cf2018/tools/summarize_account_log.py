#!/usr/bin/env python3
"""Read-only, local account-error mentions; never export log text or identity.

Default reads an existing file/stdin. --adb reads only the running original
game's recent log buffer. It never starts the game, clears logs or sends login.
"""
import argparse, datetime, hashlib, json, re, subprocess, sys, uuid
from collections import Counter
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
PACKAGE = 'com.tencent.tmgp.cfmnac'
TAG = re.compile(r'^[VDIWEF]/iMSDK\s*\(\s*\d+\s*\):\s?(.*)$')
FIELD = re.compile(r'(?<![\w\\])"?(imsdkRetCode|thirdRetCode|code)"?\s*[:=]\s*(-?\d+)(?![\w.])')
PRIMARY = {1: 'SDK_STATUS_1', 4: 'SDK_STATUS_4', 6: 'SDK_STATUS_6'}
BACKEND = {1: 'BACKEND_STATUS_1', -100: 'HTTP_AUTH_FAILURE', -111: 'HTTP_NO_CONNECTION',
           -110: 'HTTP_NETWORK_ERROR', -120: 'HTTP_PARSE_ERROR', -131: 'HTTP_CLIENT_ERROR',
           -130: 'HTTP_SERVER_ERROR', -140: 'HTTP_TIMEOUT'}
ERROR_NAMES = ('SSLHandshakeException', 'SSLPeerUnverifiedException', 'CertPathValidatorException',
               'CertificateExpiredException', 'CertificateException', 'UnknownHostException',
               'ConnectException', 'SocketTimeoutException', 'AuthFailureError',
               'NoConnectionError', 'NetworkError', 'ParseError', 'ServerError',
               'ClientError', 'TimeoutError')
ERRORS = {name: re.compile(r'(?<!\w)' + name + r'(?!\w)') for name in ERROR_NAMES}
# Only endpoint fingerprints from the exact original LocalizationSettingConfig_.
# Roles describe shipped configuration, not observed login/callback ownership.
HOST_ROLES = {
    '19f2e13a8c85347201f8a5a29379aa6aa9f67832eb7a5ab68d82feb6e87e0cdf': 'ACCOUNT_API_ENDPOINT',
    '343bca6e1806f447beb7f69f782ebc61f5fc51bfeb7cc80623160853098a413f': 'SDK_CONFIG_ENDPOINT',
    '4e3834c9262fd9aff98a57d4f3c0ef73a5e607872d2e29887184ae618496e7b5': 'ACCOUNT_API_ENDPOINT',
    '888616555cd0bf7774c9baa3b122928878092efb87c0654b5c4c577ee542c9e4': 'ACCOUNT_API_ENDPOINT',
    'c9bd0b5ed80e90ce9ea695ffe00d9337cb86624d4fd2630a04ff257f91276c15': 'SDK_CONFIG_ENDPOINT',
    'd19ee0dbbe0dd953c90728803cbb31333a6a5b592e0423d6850dc0898da82d81': 'SHARED_ACCOUNT_CONFIG_ENDPOINT',
    'dca2d537d9d44611edc2d220718f125f4c6bc2bfdd2d333a2235ae886e40fddd': 'SDK_CONFIG_ENDPOINT',
}
DNS_HOST = re.compile(r'''Unable to resolve host\s+\\?["']([A-Za-z0-9.-]{1,253})\\?["']''', re.IGNORECASE)


def dns_role(host, known=HOST_ROLES):
    canonical = host.lower().rstrip('.')
    digest = hashlib.sha256(canonical.encode('ascii')).hexdigest()
    return known.get(digest, 'OTHER_HOST_UNKNOWN_ROLE')


def summarize(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('Input exceeds the bounded log limit; no report written.')
    counts, dns_counts, accepted = Counter(), Counter(), 0
    for line in raw.decode('utf-8', errors='replace').splitlines():
        match = TAG.fullmatch(line)
        if not match:
            continue
        accepted += 1
        message = match.group(1)
        for host in DNS_HOST.findall(message):
            dns_counts[dns_role(host)] += 1
        for name, pattern in ERRORS.items():
            if pattern.search(message):
                counts[name] += 1
        for field, value in FIELD.findall(message):
            # Arbitrary numbers never reach output, including unusually long IDs.
            if len(value) > 7:
                counts['UNRECOGNIZED_STATUS'] += 1
                continue
            lookup = PRIMARY if field == 'imsdkRetCode' else BACKEND
            counts[lookup.get(int(value), 'UNRECOGNIZED_STATUS')] += 1
    return {'format': 'CF2018_ACCOUNT_LOG_MENTIONS', 'sdk_lines_examined': accepted,
            'mentions': dict(sorted(counts.items())), 'dns_host_mentions': dict(sorted(dns_counts.items())),
            'host_role_scope': 'SHIPPED_CONFIG_ALL_REGIONS_NOT_CALLBACK_ATTRIBUTION',
            'input_scope': 'SDK_TAG_ONLY_UNVERIFIED_PROCESS',
            'stage_attribution': 'UNKNOWN',
            'login_acceptance': 'NOT_ESTABLISHED',
            'limits': 'Mentions may belong to other SDK operations or older attempts; absence is not success.'}


def read_adb():
    def run(args):
        try:
            result = subprocess.run(['adb'] + args, capture_output=True, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired):
            raise ValueError('Android debug connection unavailable; pair/connect adb first.') from None
        if result.returncode:
            raise ValueError('Android log read failed; no raw error text exported.')
        return result.stdout
    pid = run(['shell', 'pidof', '-s', PACKAGE]).strip()
    if not re.fullmatch(rb'[1-9][0-9]{0,8}', pid):
        raise ValueError('Original game process is not running; no log read performed.')
    # Android limits each log entry; -t also bounds the requested entry count.
    return run(['logcat', '-d', '-t', '1500', '--pid=' + pid.decode('ascii'), '-v', 'brief'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--adb', action='store_true')
    source.add_argument('--file', type=Path)
    source.add_argument('--stdin', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=Path.home() / 'storage/downloads')
    args = parser.parse_args()
    try:
        if args.adb:
            raw = read_adb()
        elif args.file:
            with args.file.open('rb') as stream:
                raw = stream.read(MAX_BYTES + 1)
        else:
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        report = summarize(raw)
        if args.adb:
            report['input_scope'] = 'RUNNING_GAME_PID_FILTERED_LOG_BUFFER'
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
        name = 'CF2018_ACCOUNT_ERRORS_' + stamp + '_' + uuid.uuid4().hex[:8] + '.txt'
        target = args.output_dir / name
        with target.open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
        print('Saved ' + str(target))
        print('Fixed labels only; no account details, tokens, hosts or raw log lines exported.')
    except (ValueError, OSError):
        print('No report written: check adb connection, input access/size and output folder.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
