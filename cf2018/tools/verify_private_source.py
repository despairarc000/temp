"""Offline verifier for a previously identified private mirror APK.

Stdlib plus local OpenSSL. No download, game execution, upload or certificate
trust-chain claim. Only sanitized metadata is returned; originals stay local.
Embedded Android identity is pinned by the APK hash; its independent manifest
parse is recorded in sources/SOURCE_PROVENANCE.md, not reimplemented here.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import zipfile

APK_SIZE = 30884905
APK_SHA256 = '33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9'
CERT_SHA256 = 'dbfc84490cc286cb3e6cfa243c8c175dab6f33862997e6b45a2973aa41a262b4'
MEMBERS = {
    'lib/armeabi-v7a/libapollo.so': (5243704, '4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'),
    'assets/bin/Data/Managed/Assembly-CSharp.dll': (13423104, '174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9'),
    'assets/bin/Data/Managed/Assembly-CSharp-firstpass.dll': (317440, '4ac2b58a02cc1d3ad1e345d9b21dd78c758b0077c19354862792d25bcaa8ba60'),
}
SIG_NAMES = {'META-INF/MANIFEST.MF', 'META-INF/CERT.SF', 'META-INF/CERT.RSA'}


class VerificationError(ValueError):
    pass


def sha256_path(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_sections(raw):
    """Parse only the v1 manifest fields needed for the digest chain."""
    if not isinstance(raw, bytes) or len(raw) > 4 * 1024 * 1024:
        raise VerificationError('manifest input outside bound')
    sections, fields, current = [], {}, None
    for line in raw.decode('utf-8').splitlines() + ['']:
        if not line:
            if fields:
                sections.append(fields)
            fields, current = {}, None
        elif line.startswith(' '):
            if current is None:
                raise VerificationError('orphan manifest continuation')
            fields[current] += line[1:]
        else:
            name, separator, value = line.partition(': ')
            key = name.lower()
            if not separator or key in fields:
                raise VerificationError('invalid or duplicate manifest attribute')
            fields[key], current = value, key
    return sections


def _sha1_b64(raw):
    return base64.b64encode(hashlib.sha1(raw).digest()).decode('ascii')


def verify_jar_digests(archive):
    """Verify digest links only; cryptographic CMS verification is separate."""
    entries = archive.infolist()
    names = [i.filename for i in entries]
    if len(names) != len(set(names)):
        raise VerificationError('duplicate ZIP entry')
    manifest = archive.read('META-INF/MANIFEST.MF')
    sf = archive.read('META-INF/CERT.SF')
    sf_sections = manifest_sections(sf)
    if not sf_sections or sf_sections[0].get('sha1-digest-manifest') != _sha1_b64(manifest):
        raise VerificationError('signature-file manifest digest mismatch')
    sections = manifest_sections(manifest)
    if not sections:
        raise VerificationError('missing manifest main section')
    signed = set()
    for section in sections[1:]:
        name, digest = section.get('name'), section.get('sha1-digest')
        if not name or not digest or name in signed:
            raise VerificationError('invalid or duplicate signed entry')
        if name not in names or _sha1_b64(archive.read(name)) != digest:
            raise VerificationError('signed entry digest mismatch')
        signed.add(name)
    payloads = {i.filename for i in entries if not i.is_dir()} - SIG_NAMES
    if signed != payloads:
        raise VerificationError('unsigned or omitted payload entry')
    return len(signed)


def elf_identity(raw):
    if len(raw) < 52 or raw[:7] != b'\x7fELF\x01\x01\x01':
        raise VerificationError('ELF32 little-endian identity mismatch')
    file_type, machine, version = struct.unpack_from('<HHI', raw, 16)
    flags = struct.unpack_from('<I', raw, 36)[0]
    if file_type != 3 or machine != 40 or version != 1 or flags >> 24 != 5:
        raise VerificationError('ARM EABI5 shared-object identity mismatch')
    return {'class': 32, 'endianness': 'little', 'machine': 'ARM',
            'type': 'DYN', 'eabi': 5, 'flags': flags}


def verify_cms(archive):
    openssl = shutil.which('openssl')
    if not openssl:
        raise VerificationError('local OpenSSL unavailable; CMS unrun')
    private = Path(__file__).parent / 'private'
    private.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=private) as directory:
        directory = Path(directory)
        rsa, sf = directory / 'sig.der', directory / 'sig.sf'
        pem, cert = directory / 'cert.pem', directory / 'cert.der'
        rsa.write_bytes(archive.read('META-INF/CERT.RSA'))
        sf.write_bytes(archive.read('META-INF/CERT.SF'))
        commands = [
            [openssl, 'cms', '-verify', '-inform', 'DER', '-in', str(rsa),
             '-content', str(sf), '-noverify', '-binary', '-out', str(directory / 'verified.sf')],
            [openssl, 'pkcs7', '-inform', 'DER', '-in', str(rsa), '-print_certs', '-out', str(pem)],
            [openssl, 'x509', '-in', str(pem), '-outform', 'DER', '-out', str(cert)],
        ]
        for command in commands:
            try:
                subprocess.run(command, check=True, capture_output=True, timeout=15)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise VerificationError('OpenSSL verification operation failed') from exc
        if pem.read_bytes().count(b'-----BEGIN CERTIFICATE-----') != 1:
            raise VerificationError('unexpected signing certificate count')
        if sha256_path(cert) != CERT_SHA256:
            raise VerificationError('signing certificate fingerprint mismatch')
    return {'cms_signature': 'PASS', 'certificate_sha256': CERT_SHA256,
            'certificate_trust_chain': 'NOT_VALIDATED'}


def verify(apk_path, *, extracted_library=None):
    apk_path = Path(apk_path)
    if apk_path.stat().st_size != APK_SIZE or sha256_path(apk_path) != APK_SHA256:
        raise VerificationError('pinned APK size/hash mismatch')
    with zipfile.ZipFile(apk_path) as archive:
        bad_crc = archive.testzip()
        if bad_crc is not None:
            raise VerificationError('APK CRC mismatch')
        digests = verify_jar_digests(archive)
        artifacts = []
        for name, (size, expected) in MEMBERS.items():
            raw = archive.read(name)
            if len(raw) != size or hashlib.sha256(raw).hexdigest() != expected:
                raise VerificationError('pinned APK member size/hash mismatch')
            artifacts.append({'apk_member': name, 'bytes': size, 'sha256': expected})
        native = elf_identity(archive.read('lib/armeabi-v7a/libapollo.so'))
        if 'lib/armeabi-v7a/libmono.so' not in archive.namelist():
            raise VerificationError('expected Mono runtime missing')
        signature = verify_cms(archive)
    if extracted_library is not None:
        size, expected = MEMBERS['lib/armeabi-v7a/libapollo.so']
        if Path(extracted_library).stat().st_size != size or sha256_path(extracted_library) != expected:
            raise VerificationError('extracted library differs from pinned APK member')
    return {'apk_bytes': APK_SIZE, 'apk_sha256': APK_SHA256,
            'identity_basis': 'pinned APK hash; separate embedded-manifest receipt',
            'signed_entries': digests, 'artifacts': artifacts, 'native': native,
            'signature': signature, 'phone_build_equality': 'UNVERIFIED',
            'whole_xapk_and_obb': 'NOT_VERIFIED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path)
    parser.add_argument('--library', type=Path)
    args = parser.parse_args()
    if args.apk is None:
        if args.library is not None:
            parser.error('--library requires --apk')
        print('Inactive: supply --apk for explicit offline private-source verification.')
        return
    print(json.dumps(verify(args.apk, extracted_library=args.library), indent=2))


if __name__ == '__main__':
    main()
