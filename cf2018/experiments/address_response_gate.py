"""Offline-only strict Apollo QueryAddrInfo legacy Thrift response preflight.

No network, authentication, game execution, or native parser parity. Structural
candidate and session-correlation checks, not validated application acceptance.

Coordinator integration of CF18-05 original code with native-required reason
field correction; see coordination/ADDRESS_NATIVE_MATRIX.json and Vault trace.
"""
from dataclasses import dataclass
from ipaddress import ip_address

# The original client sends a colon-qualified request; the response's exact
# method-name policy has not yet been confirmed in a live receiver. Allow only
# these two evidence-backed structural controls for offline preflight.
ALLOWED_ADDRESS_METHODS = frozenset(('QueryAddrInfo', 'QueryAddrSvr:QueryAddrInfo'))

class ResponseError(ValueError):
    pass

@dataclass(frozen=True)
class ParsedResponse:
    method: str
    message_type: int
    sequence: int
    result: int
    addresses: tuple
    reason_present: bool

class Reader:
    def __init__(self, data, cap=8192):
        if not isinstance(data, bytes) or not 1 <= len(data) <= cap:
            raise ResponseError('input absent or exceeds budget')
        self.data = data
        self.pos = 0
    def take(self, n):
        if n < 0 or n > len(self.data) - self.pos:
            raise ResponseError('truncated input')
        out = self.data[self.pos:self.pos+n]
        self.pos += n
        return out
    def num(self, n, signed=False):
        return int.from_bytes(self.take(n), 'big', signed=signed)
    def string(self, cap=1024):
        n = self.num(4, signed=True)
        if not 0 <= n <= cap:
            raise ResponseError('string exceeds budget')
        try:
            return self.take(n).decode('utf-8')
        except UnicodeDecodeError as exc:
            raise ResponseError('invalid UTF-8') from exc
    def field(self):
        t = self.num(1)
        if t == 0:
            return 0, 0
        return t, self.num(2, signed=True)

def _struct(reader, fields, *, field_label):
    seen = set()
    while True:
        kind, fid = reader.field()
        if kind == 0:
            break
        if (fid, kind) not in fields:
            raise ResponseError(f'unsupported {field_label} field/type')
        if fid in seen:
            raise ResponseError(f'duplicate {field_label} field')
        seen.add(fid)
        yield fid

def parse_response(data):
    """Strict read of SYNTHETIC unversioned TBinaryProtocol QueryAddrInfo reply.

    Outer GCloud connector/framing is not included or demonstrated.
    """
    rd = Reader(data)
    method = rd.string(96)
    if method not in ALLOWED_ADDRESS_METHODS:
        raise ResponseError('unexpected method')
    msg_type = rd.num(1)
    if msg_type != 2:
        raise ResponseError('not an RPC reply')
    sequence = rd.num(8)
    success_seen = False
    result = None
    reason_seen = False
    addresses = []
    for _ in _struct(rd, {(0, 12)}, field_label='result wrapper'):
        success_seen = True
        for nested_id in _struct(rd, {(1, 8), (2, 11), (3, 15)}, field_label='response'):
            if nested_id == 1:
                result = rd.num(4, signed=True)
            elif nested_id == 2:
                rd.string()
                reason_seen = True
            elif nested_id == 3:
                element_type, n = rd.num(1), rd.num(4, signed=True)
                if element_type != 12 or not 0 <= n <= 32:
                    raise ResponseError('invalid addresses list')
                for _ in range(n):
                    host = None
                    port = None
                    for item_id in _struct(rd, {(1, 11), (2, 8)}, field_label='address'):
                        if item_id == 1:
                            host = rd.string(128)
                        else:
                            port = rd.num(4, signed=True)
                    if host is None or port is None:
                        raise ResponseError('incomplete address')
                    addresses.append((host, port))
    if not success_seen or result is None:
        raise ResponseError('missing success wrapper or result field')
    if not reason_seen:
        raise ResponseError('missing native-required reason string field')
    if rd.pos != len(data):
        raise ResponseError('trailing data')
    return ParsedResponse(method, msg_type, sequence, result, tuple(addresses), reason_seen)

def assess_response(response, *, pending_sequences):
    """Conservative local candidate policy; not native/app acceptance."""
    if not isinstance(response, ParsedResponse):
        raise TypeError('ParsedResponse required')
    if response.sequence not in pending_sequences:
        return 'REJECT_NO_PENDING_SEQUENCE'
    if response.message_type != 2 or response.method not in ALLOWED_ADDRESS_METHODS:
        return 'REJECT_UNEXPECTED_RPC'
    if response.result != 0:
        return 'REJECT_RESPONSE_RESULT'
    if not response.addresses:
        return 'WAIT_NO_ADDRESS_CANDIDATES'
    for host, port in response.addresses:
        if not 1 <= port <= 65535:
            return 'REJECT_PORT_POLICY'
        try:
            ip_address(host)
        except ValueError:
            if not host or len(host) > 128 or any(x.isspace() for x in host):
                return 'REJECT_HOST_POLICY'
    return 'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE'
