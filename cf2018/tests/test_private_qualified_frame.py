"""Private-source gated full TGCP frame checks, all message data synthetic."""
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from test_qualified_address_request import candidate

def vint(n):
    result=bytearray()
    while n>127:
        result.append((n&127)|128);n>>=7
    return bytes(result)+bytes([n])

def field(n,kind,data):
    tag=vint(n<<4|kind)
    if kind==5:return tag+len(data).to_bytes(4,'big')+data
    if kind==0:return tag+vint(data)
    raise ValueError('fixture types limited')

def routed_frame(body,route=b'QueryAddrSvr',seq=1):
    base=field(7,0,seq)+field(9,0,len(body))
    routes=field(4,5,field(4,5,field(1,5,route)))
    ext=field(0x4013,5,routes)
    outer=field(1,5,base)+field(2,5,ext)
    return b'\x43\x66\xaa'+(5+len(outer)).to_bytes(4,'big')+outer+body

class PrivateFullFrameTest(unittest.TestCase):
    def test_original_tgcp_classifier_and_new_qualified_classifier(self):
        source=os.environ.get('CF18_V38_SOURCE')
        if not source:self.skipTest('exact private V3.8 source required')
        sys.path.insert(0,str(Path(source)))
        from routed_body_diagnostic import inspect_v38_frame
        from qualified_frame_inspector import inspect_qualified_frame
        for n,unit in ((3,2),(8,0x1000002)):
            with self.subTest(service_size=n):
                sample=routed_frame(candidate(n,unit_id=unit))
                self.assertEqual(inspect_v38_frame(sample)['sequence_prefix'],'MATCH')
                self.assertEqual(inspect_v38_frame(sample)['known_address_route'],'MATCH')
                self.assertEqual(inspect_qualified_frame(sample)[
                    'qualified_address_request'],'COMPLETE_STRUCTURAL_CANDIDATE')
                self.assertEqual(inspect_qualified_frame(routed_frame(
                    candidate(n,unit_id=unit),b'OtherRoute'))[
                    'qualified_address_request'],'NOT_COMPARABLE')
                self.assertEqual(inspect_qualified_frame(routed_frame(
                    candidate(n,unit_id=unit),seq=3))[
                    'qualified_address_request'],'NOT_COMPARABLE')

if __name__=='__main__':unittest.main()
