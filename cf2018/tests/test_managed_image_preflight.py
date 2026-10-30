import importlib.util
from pathlib import Path
import struct
import unittest

SPEC=importlib.util.spec_from_file_location('preflight',Path(__file__).resolve().parents[1]/'tools/managed_image_preflight.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)


def synthetic_image():
    b=bytearray(1024)
    def w32(o,v):struct.pack_into('<I',b,o,v)
    def w16(o,v):struct.pack_into('<H',b,o,v)
    b[:2]=b'MZ';w32(60,128);b[128:132]=b'PE\0\0'
    w16(134,1);w16(148,224);opt=152
    w16(opt,0x10b);w32(opt+92,16);w32(opt+96+14*8,0x2000);w32(opt+96+14*8+4,72)
    sec=opt+224;w32(sec+12,0x2000);w32(sec+16,512);w32(sec+20,512)
    w32(512,72);w32(520,0x2080);w32(524,128);w32(528,1)
    b[640:644]=b'BSJB';w32(652,4);b[656:660]=b'v1\0\0';w16(662,1)
    w32(664,40);w32(668,24);b[672:676]=b'#~\0\0'
    return bytes(b)


class PreflightTests(unittest.TestCase):
    def test_non_pe_is_classified_without_assuming_why(self):
        r=M.inspect_image(b'opaque synthetic bytes')
        self.assertEqual(r['status'],'STORED_NON_PE')
        self.assertFalse(r['runtime_load_verified'])

    def test_synthetic_managed_headers_not_a_load_or_il_verification(self):
        r=M.inspect_image(synthetic_image())
        self.assertEqual(r['status'],'MANAGED_HEADERS_PRESENT')
        self.assertFalse(r['runtime_load_verified'])

    def test_truncated_or_invalid_pe_refused(self):
        for data in (b'MZ', b'MZ'+bytes(64), synthetic_image()[:500]):
            self.assertEqual(M.inspect_image(data)['status'],'MALFORMED_MANAGED_HEADERS')

    def test_out_of_range_cli_or_metadata_refused(self):
        for off in (360,520,524,652,664,668):
            b=bytearray(synthetic_image());struct.pack_into('<I',b,off,0xffffffff)
            self.assertEqual(M.inspect_image(bytes(b))['status'],'MALFORMED_MANAGED_HEADERS')

    def test_diff_reports_offsets_without_mutating_or_dumping_bytes(self):
        a=b'abcdefgh';b=b'abcXefgh'
        r=M.compare_bytes(a,b)
        self.assertEqual((r['changed_positions'],r['first_changed'],r['last_changed']),(1,3,3))
        self.assertEqual((a,b),(b'abcdefgh',b'abcXefgh'))

    def test_identity_and_length_only_changes(self):
        self.assertTrue(M.compare_bytes(b'abcd',b'abcd')['identical'])
        self.assertEqual(M.compare_bytes(b'abcd',b'abcdef')['changed_positions'],2)

    def test_budgets_checked_before_parsing(self):
        for data in (b'',bytearray(b'x'),bytes(M.LIMIT+1)):
            with self.assertRaises(ValueError):M.inspect_image(data)
