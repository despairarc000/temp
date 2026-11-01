"""Synthetic evidence for original QueryAddrSvr:QueryAddrInfo qualified method."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from qualified_address_request import classify_known_qualified_query,QUALIFIED_NAME
from routed_body_diagnostic import diagnose_body

def candidate(service_size,unit_id=2,last=b'A'):
    if type(service_size) is not int or not 1<=service_size<=128:
        raise ValueError('service length')
    if type(unit_id) is not int or not 0<=unit_id<2**64:
        raise ValueError('unit id')
    name=QUALIFIED_NAME
    service=b'A'*(service_size-1)+last
    header=len(name).to_bytes(4,'big')+name+b'\x01'+(1).to_bytes(8,'big')
    fields=(bytes.fromhex('0c00010a0001')+(1).to_bytes(8,'big')+
       bytes.fromhex('0a0002')+unit_id.to_bytes(8,'big')+
       bytes.fromhex('0b0003')+len(service).to_bytes(4,'big')+
       service+b'\x00\x00')
    return (1).to_bytes(4,'big')+header+fields

class QualifiedAddressRequestTests(unittest.TestCase):
    def test_all_reported_phone_shape_bands_can_fit_without_extra_wrapper(self):
        a=candidate(3,2)
        b=candidate(8,0x1000002,b'B')
        self.assertEqual((len(a),len(b)),(80,85))
        first=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)
        suffix=next((i for i,(x,y) in enumerate(zip(a[::-1],b[::-1])) if x!=y),None)
        self.assertEqual((first,suffix),(64,2))
        for body in (a,b):
            self.assertEqual(diagnose_body(body,1),{
                'sequence_prefix':'MATCH','legacy_at_start':'METHOD_BYTES_POLICY',
                'legacy_after_sequence':'METHOD_BYTES_POLICY'})
            self.assertEqual(classify_known_qualified_query(body,1)[
                'qualified_address_request'],'COMPLETE_STRUCTURAL_CANDIDATE')

    def test_colon_is_what_existing_lexical_policy_rejects(self):
        raw=candidate(3)
        self.assertEqual(raw[4:8],b'\x00\x00\x00\x1a')
        self.assertEqual(raw[8:34],b'QueryAddrSvr:QueryAddrInfo')
        self.assertEqual(diagnose_body(raw,1)['legacy_after_sequence'],
                         'METHOD_BYTES_POLICY')
        changed=raw.replace(b':',b'.',1)
        self.assertEqual(diagnose_body(changed,1)['legacy_after_sequence'],
                         'LEGACY_HEADER_PLAUSIBLE')
        self.assertEqual(classify_known_qualified_query(changed,1)[
            'qualified_address_request'],'NOT_IDENTIFIED')

    def test_corruption_and_truncation_rejected(self):
        raw=candidate(3)
        for bad in (raw[:-1],raw[:-2]+b'\xfe\x00',
                    raw[:43]+b'\x0d'+raw[44:],
                    raw[:71]+b'\xff'+raw[72:],
                    raw[:4]+b'\x00\x00\x00\x19'+raw[8:],
                    raw[:34]+b'\x03'+raw[35:]):
            self.assertEqual(classify_known_qualified_query(bad,1)[
                'qualified_address_request'],'NOT_IDENTIFIED')

    def test_sequence_mismatch_rejected(self):
        result=classify_known_qualified_query(candidate(3),4)
        self.assertEqual(result['sequence_prefix'],'MISMATCH')
        self.assertEqual(result['qualified_address_request'],'NOT_IDENTIFIED')

    def test_bounds(self):
        for body,seq in ((bytearray(80),1),(b'X'*8193,1),(b'X',True),
                         (b'X',-1),(b'X',2**32)):
            with self.assertRaises(ValueError):
                classify_known_qualified_query(body,seq)
        self.assertEqual(classify_known_qualified_query(b'\x00',1)[
            'qualified_address_request'],'NOT_COMPARABLE')

if __name__=='__main__':unittest.main()
