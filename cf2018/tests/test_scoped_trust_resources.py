import sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from scoped_trust_resources import (chunk,chunks,make_pool,pool_values,extend_pool,
                                   append_resources,manifest_reference,trust_xml,NONE)


class BinaryControls(unittest.TestCase):
    def test_unicode_string_indices_preserved_on_append(self):
        values=['','synthetic','café','測試','😀','x'*33000]
        before=make_pool(values)
        after,index=extend_pool(before,['new'])
        self.assertEqual(index,len(values))
        self.assertEqual(pool_values(after)[0],values+['new'])

    def test_style_data_and_offsets_preserved(self):
        styles=struct.pack('<III',NONE,NONE,NONE)
        before=make_pool(['synthetic'],struct.pack('<I',0),styles)
        after,_=extend_pool(before,['new'])
        self.assertEqual(pool_values(after)[1:3],pool_values(before)[1:3])

    def test_truncated_and_overrun_chunks_refused(self):
        for raw in [b'abc',struct.pack('<HHI',1,8,500),struct.pack('<HHI',1,20,8)]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):list(chunks(raw,0))

    def test_unrelated_resource_package_refused(self):
        with self.assertRaises(ValueError):append_resources(chunk(2,struct.pack('<I',2),b''))

    def test_unrelated_manifest_refused(self):
        with self.assertRaises(ValueError):manifest_reference(chunk(2,b'',b''),0x7f010000)

    def test_existing_trust_override_requires_review(self):
        raw=chunk(3,b'',make_pool(['networkSecurityConfig']))
        with self.assertRaisesRegex(ValueError,'existing trust configuration'):
            manifest_reference(raw,0x7f010000)

    def test_host_scope_rejects_url_wildcard_empty_and_excess(self):
        for hosts in [[],['https://synthetic.invalid'],['*.synthetic.invalid'],['synthetic.invalid']*9]:
            with self.subTest(hosts=hosts),self.assertRaises(ValueError):trust_xml(hosts,0x7f020000)

    def test_manifest_attribute_addition_is_unique(self):
        pool=make_pool(['application','http://schemas.android.com/apk/res/android'])
        resource_map=chunk(0x180,b'',struct.pack('<I',0))
        element=chunk(0x102,struct.pack('<II',1,NONE),struct.pack('<IIHHHHHH',NONE,0,20,20,0,0,0,0))
        raw=chunk(3,b'',pool+resource_map+element)
        out=manifest_reference(raw,0x7f220000)
        elements=[c for _,k,c in chunks(out,8) if k==0x102]
        self.assertEqual(struct.unpack_from('<H',elements[0],28)[0],1)
        self.assertEqual(struct.unpack_from('<I',elements[0],52)[0],0x7f220000)
        with self.assertRaisesRegex(ValueError,'existing trust configuration'):
            manifest_reference(out,0x7f220000)


if __name__=='__main__':unittest.main()
