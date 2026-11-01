"""Narrow fixed-label classifier for the original colon-qualified address RPC.
Structural candidate only: does not establish the phone's producer or login.
"""
QUALIFIED_NAME=b'QueryAddrSvr:QueryAddrInfo'
MAX_BODY=8192
MAX_SERVICE=128

def classify_known_qualified_query(body,packet_sequence):
    if type(body) is not bytes or not 0<=len(body)<=MAX_BODY:
        raise ValueError('bounded bytes required')
    if type(packet_sequence) is not int or not 0<=packet_sequence<2**32:
        raise ValueError('validated packet sequence required')
    if len(body)<4:
        return {'sequence_prefix':'SHORT','qualified_address_request':'NOT_COMPARABLE'}
    same=body[:4]==packet_sequence.to_bytes(4,'big')
    return {
        'sequence_prefix':'MATCH' if same else 'MISMATCH',
        'qualified_address_request':('COMPLETE_STRUCTURAL_CANDIDATE'
            if same and _accept(body) else 'NOT_IDENTIFIED'),
    }

def _accept(body):
    p=4
    if len(body)<4+4+26+1+8+6+8+3+8+3+4+2:
        return False
    n=int.from_bytes(body[p:p+4],'big');p+=4
    if n!=len(QUALIFIED_NAME) or body[p:p+n]!=QUALIFIED_NAME:
        return False
    p+=n
    if body[p]!=1:
        return False
    p+=1+8
    if body[p:p+6]!=bytes.fromhex('0c00010a0001'):
        return False
    p+=6+8
    if body[p:p+3]!=bytes.fromhex('0a0002'):
        return False
    p+=3+8
    if body[p:p+3]!=bytes.fromhex('0b0003'):
        return False
    p+=3
    string_length=int.from_bytes(body[p:p+4],'big');p+=4
    return (0<=string_length<=MAX_SERVICE and
        p+string_length+2==len(body) and body[-2:]==b'\x00\x00')
