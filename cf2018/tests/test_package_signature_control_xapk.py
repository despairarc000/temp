import contextlib,importlib.util,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

P=Path(__file__).resolve().parents[1]/'tools/package_signature_control_xapk.py'
spec=importlib.util.spec_from_file_location('xapk',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
OBB='Android/obb/com.tencent.tmgp.cfmnac/main.11.com.tencent.tmgp.cfmnac.obb'

class Packaging(unittest.TestCase):
    def fixture(self,root,corrupt=False,extra=False):
        download=root/'storage/shared/Download';download.mkdir(parents=True)
        stage=root/'cf2018_control_test';stage.mkdir()
        original=b'synthetic-original-apk';control=b'synthetic-signed-control-apk';obb=b'synthetic resource'*100
        manifest={'xapk_version':2,'package_name':'com.tencent.tmgp.cfmnac','total_size':len(original)+len(obb),
                  'apks':[{'file':'base.apk','size':str(len(original)),'sha256':m.sha(original)}],
                  'split_apks':[{'file':'base.apk','id':'base'}],
                  'expansions':[{'file':OBB,'size':len(obb)}]}
        (stage/'control.apk').write_bytes(control)
        with ZipFile(download/'Original.xapk','w') as z:
            z.writestr('base.apk',b'wrong' if corrupt else original)
            z.writestr(OBB,obb);z.writestr('icon.png',b'synthetic icon');z.writestr('manifest.json',json.dumps(manifest))
            if extra:z.writestr('unexpected',b'no')
        return download,original,control,obb,manifest

    def invoke(self,root,original,control,obb):
        with patch.object(m.Path,'home',return_value=root),patch.multiple(m,ORIGINAL=m.sha(original),CONTROL=m.sha(control),APK_BYTES=len(original),OBB_BYTES=len(obb)),contextlib.redirect_stdout(io.StringIO()):
            m.main()

    def test_container_payload_preserved_and_metadata_updated(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,manifest=self.fixture(root)
            before=(download/'Original.xapk').read_bytes();self.invoke(root,original,control,obb)
            target=next(download.glob('CF2018_SIGNATURE_CONTROL_*.xapk'))
            with ZipFile(target) as z:
                self.assertEqual(z.read('base.apk'),control);self.assertEqual(z.read(OBB),obb)
                self.assertEqual(z.read('icon.png'),b'synthetic icon')
                meta=json.loads(z.read('manifest.json'))
                self.assertEqual(meta['total_size'],len(control)+len(obb))
                self.assertEqual(meta['apks'][0]['sha256'],m.sha(control))
                self.assertEqual(meta['apks'][0]['size'],str(len(control)))
                self.assertEqual(meta['expansions'],manifest['expansions'])
                self.assertEqual(meta['xapk_version'],2)
                self.assertNotIn('manifest_version',meta)
                self.assertEqual(meta['split_apks'],manifest['split_apks'])
            self.assertEqual((download/'Original.xapk').read_bytes(),before)
            receipt=json.loads(target.with_suffix('.txt').read_text())
            self.assertTrue(receipt['all_output_payloads_verified']);self.assertFalse(receipt['installation_performed'])

    def test_wrong_original_refused_before_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,_=self.fixture(root,corrupt=True)
            with self.assertRaisesRegex(ValueError,'Original APK'):self.invoke(root,original,control,obb)
            self.assertEqual(list(download.glob('CF2018*')),[])

    def test_unexpected_container_entry_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,_=self.fixture(root,extra=True)
            with self.assertRaisesRegex(ValueError,'layout'):self.invoke(root,original,control,obb)
            self.assertEqual(list(download.glob('CF2018*')),[])

    def test_wrong_control_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,_=self.fixture(root)
            (root/'cf2018_control_test/control.apk').write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError,'Control APK'):self.invoke(root,original,control,obb)
            self.assertEqual(list(download.glob('CF2018*')),[])

    def test_repeated_runs_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,_=self.fixture(root)
            self.invoke(root,original,control,obb);self.invoke(root,original,control,obb)
            self.assertEqual(len(list(download.glob('CF2018_SIGNATURE_CONTROL_*.xapk'))),2)

    def rewrite_manifest(self,download,change):
        path=download/'Original.xapk'
        with ZipFile(path) as z:items={n:z.read(n) for n in z.namelist()}
        meta=json.loads(items['manifest.json']);change(meta);items['manifest.json']=json.dumps(meta).encode()
        with ZipFile(path,'w') as z:
            for n,b in items.items():z.writestr(n,b)

    def test_legacy_schema_retained_without_invented_xapk_field(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,_=self.fixture(root)
            self.rewrite_manifest(download,lambda v:v.update(manifest_version=v.pop('xapk_version')))
            self.invoke(root,original,control,obb)
            with ZipFile(next(download.glob('CF2018_SIGNATURE_CONTROL_*.xapk'))) as z:
                meta=json.loads(z.read('manifest.json'));self.assertEqual(meta['manifest_version'],2)
                self.assertNotIn('xapk_version',meta)

    def test_conflicting_schema_versions_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);download,original,control,obb,_=self.fixture(root)
            self.rewrite_manifest(download,lambda v:v.update(manifest_version=1))
            with self.assertRaisesRegex(ValueError,'Conflicting'):self.invoke(root,original,control,obb)
            self.assertEqual(list(download.glob('CF2018*')),[])

if __name__=='__main__':unittest.main()
