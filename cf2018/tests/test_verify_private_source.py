"""Synthetic integrity-chain controls, plus explicit optional private-source checks."""
import base64
import hashlib
import io
import os
from pathlib import Path
import struct
import shutil
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import warnings
import zipfile
from verify_private_source import (VerificationError, manifest_sections,
    verify_jar_digests, elf_identity, verify_cms, verify, APK_SIZE)


def fixture(*, payload=b'abc', signed_payload=b'abc', extra=False,
            duplicate=False, duplicate_section=False, manifest_tamper=False,
            folded=False, omit=False):
    name = 'synthetic.bin'
    rendered_name = 'synthetic.\r\n bin' if folded else name
    digest = base64.b64encode(hashlib.sha1(signed_payload).digest()).decode()
    section = f'Name: {rendered_name}\r\nSHA1-Digest: {digest}\r\n\r\n'.encode()
    manifest = b'Manifest-Version: 1.0\r\n\r\n' + section
    if duplicate_section:
        manifest += section
    sf_digest = base64.b64encode(hashlib.sha1(manifest).digest())
    sf = b'Signature-Version: 1.0\r\nSHA1-Digest-Manifest: ' + sf_digest + b'\r\n\r\n'
    if manifest_tamper:
        manifest = manifest.replace(b'Manifest-Version: 1.0', b'Manifest-Version: 1.1')
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as z:
        z.writestr('META-INF/MANIFEST.MF', manifest)
        z.writestr('META-INF/CERT.SF', sf)
        z.writestr('META-INF/CERT.RSA', b'synthetic unsigned placeholder; never a CMS success')
        if not omit:
            z.writestr(name, payload)
        if extra:
            z.writestr('extra.bin', b'extra synthetic payload')
        if duplicate:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                z.writestr(name, payload)
    output.seek(0)
    return zipfile.ZipFile(output)


class IntegrityControls(unittest.TestCase):
    def test_independent_abc_digest_link_is_not_cms_verification(self):
        with fixture() as archive:
            self.assertEqual(verify_jar_digests(archive), 1)

    def test_changed_payload_rejected_even_with_intact_manifest_chain(self):
        with fixture(payload=b'abd') as archive:
            with self.assertRaisesRegex(VerificationError, 'entry digest'):
                verify_jar_digests(archive)

    def test_manifest_mutation_rejected_by_signature_file_link(self):
        with fixture(manifest_tamper=True) as archive:
            with self.assertRaisesRegex(VerificationError, 'manifest digest'):
                verify_jar_digests(archive)

    def test_unsigned_extra_payload_rejected(self):
        with fixture(extra=True) as archive:
            with self.assertRaisesRegex(VerificationError, 'unsigned or omitted'):
                verify_jar_digests(archive)

    def test_missing_signed_payload_rejected(self):
        with fixture(omit=True) as archive:
            with self.assertRaisesRegex(VerificationError, 'entry digest'):
                verify_jar_digests(archive)

    def test_duplicate_zip_entry_rejected(self):
        with fixture(duplicate=True) as archive:
            with self.assertRaisesRegex(VerificationError, 'duplicate ZIP'):
                verify_jar_digests(archive)

    def test_duplicate_signed_section_rejected(self):
        with fixture(duplicate_section=True) as archive:
            with self.assertRaisesRegex(VerificationError, 'duplicate signed'):
                verify_jar_digests(archive)

    def test_folded_manifest_name_matches_zip_name(self):
        with fixture(folded=True) as archive:
            self.assertEqual(verify_jar_digests(archive), 1)

    def test_ambiguous_manifest_attributes_and_orphan_fold_rejected(self):
        for raw in (b'Name: a\r\nname: b\r\n', b' continuation\r\n', b'broken\r\n'):
            with self.subTest(raw=raw):
                with self.assertRaises(VerificationError):
                    manifest_sections(raw)

    def test_elf_isa_negative_controls(self):
        header = bytearray(52)
        header[:7] = b'\x7fELF\x01\x01\x01'
        struct.pack_into('<HHI', header, 16, 3, 40, 1)
        struct.pack_into('<I', header, 36, 5 << 24)
        self.assertEqual(elf_identity(header)['machine'], 'ARM')
        for offset, value in ((4, 2), (5, 2), (18, 62), (16, 2), (39, 4)):
            with self.subTest(offset=offset):
                changed = bytearray(header)
                changed[offset] = value
                with self.assertRaises(VerificationError):
                    elf_identity(changed)

    @unittest.skipUnless(shutil.which('openssl'), 'local OpenSSL required')
    def test_invalid_cms_is_not_accepted_from_passing_digest_links(self):
        with fixture() as archive:
            self.assertEqual(verify_jar_digests(archive), 1)
            with self.assertRaisesRegex(VerificationError, 'OpenSSL verification'):
                verify_cms(archive)

    def test_wrong_apk_refused_before_zip_interpretation(self):
        private = Path(__file__).parent / 'private'
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as directory:
            p = Path(directory) / 'synthetic.bin'
            p.write_bytes(b'abc')
            with self.assertRaisesRegex(VerificationError, 'pinned APK'):
                verify(p)
            with p.open('wb') as f:
                f.truncate(APK_SIZE)
            with self.assertRaisesRegex(VerificationError, 'pinned APK'):
                verify(p)


@unittest.skipUnless(os.environ.get('CF18_APK_SOURCE'), 'explicit private APK path required')
class PrivateSourceControls(unittest.TestCase):
    def test_actual_pinned_apk_cms_and_every_signed_entry(self):
        receipt = verify(os.environ['CF18_APK_SOURCE'])
        self.assertEqual(receipt['signed_entries'], 1212)
        self.assertEqual(receipt['signature']['cms_signature'], 'PASS')
        self.assertEqual(receipt['signature']['certificate_trust_chain'], 'NOT_VALIDATED')

    def test_extracted_library_mismatch_rejected(self):
        private = Path(__file__).parent / 'private'
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as directory:
            p = Path(directory) / 'synthetic.bin'
            with p.open('wb') as f:
                f.truncate(5243704)
            with self.assertRaisesRegex(VerificationError, 'extracted library differs'):
                verify(os.environ['CF18_APK_SOURCE'], extracted_library=p)


if __name__ == '__main__':
    unittest.main()
