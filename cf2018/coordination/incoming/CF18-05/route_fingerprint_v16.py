"""Privacy-minimal CF2018 0x4013 classifier; NEVER saves raw routed data.

Detects tightly bounded, allowlisted Thrift RPC method signatures; it cannot
prove encryption status, authenticated session, or actual application handling.
"""
from __future__ import annotations

# Source-provenance: pinned Apollo contains these named service methods.
ALLOWLIST = (
    b'QueryAddrInfo', b'GetUpdateInfo', b'ReqUpdateVersion',
    b'get_server_dirtree_all', b'get_server_dirtree_by_id',
    b'get_server_by_ids',
)
MAX_FRAME = 4096
MAX_SCAN = 96


def _classify_method(body: bytes) -> dict:
    """At most 96 offsets, legacy name-length/type/sequence; return labels only."""
    matches = []
    for offset in range(min(len(body), MAX_SCAN)):
        if offset + 4 > len(body):
            break
        size = int.from_bytes(body[offset:offset + 4], 'big')
        if not 1 <= size <= 64:
            continue
        tail = offset + 4 + size
        if tail + 1 + 8 > len(body):
            continue
        # Native-protocol hypothesis: unversioned TBinary method name, type,
        # 64-bit seq. Never log a sequence number, string or arbitrary bytes.
        if body[tail] not in (1, 4):
            continue
        for name in ALLOWLIST:
            if size == len(name) and body[offset + 4:tail] == name:
                matches.append((name.decode('ascii'), offset, body[tail]))
    # Deliberately do not pick arbitrary name when more than one plausible match.
    if len(matches) == 1:
        name, offset, typ = matches[0]
        return {'rpc_hint': name, 'rpc_offset': offset,
                'rpc_type_hint': 'CALL' if typ == 1 else 'ONEWAY',
                'rpc_confidence': 'ALLOWLISTED_LEGACY_SIGNATURE_ONLY'}
    return {'rpc_hint': 'AMBIGUOUS' if matches else 'NOT_IDENTIFIED',
            'rpc_offset': None, 'rpc_type_hint': 'UNKNOWN',
            'rpc_confidence': 'NO_UNIQUE_ALLOWLISTED_SIGNATURE'}


def inspect_routed_frame(frame: bytes, structure: dict) -> dict:
    """Classifies one complete sanitized client-frame result, returning metadata only.

    Existing v1.5 inspect_client_frame validates framing and header. Use that
    *before* calling this; never interpret any auth/SYN body here.
    """
    if not isinstance(frame, bytes) or not isinstance(structure, dict):
        raise TypeError('bytes and validated frame metadata required')
    if len(frame) > MAX_FRAME or frame[:3] != b'\x43\x66\xaa':
        raise ValueError('not a bounded known client frame')
    if structure.get('extension_fields') != [[0x4013, 1]]:
        raise ValueError('only exact 0x4013 routed client frames supported')
    hlen = structure.get('header_bytes')
    size = structure.get('body_bytes')
    if type(hlen) is not int or type(size) is not int or hlen < 5 or size < 0:
        raise ValueError('invalid metadata lengths')
    start = 2 + hlen
    if len(frame) != start + size or int.from_bytes(frame[3:7], 'big') != hlen:
        raise ValueError('inconsistent client frame bounds')
    body = frame[start:]
    if not body:
        envelope_hint = 'EMPTY'
    elif len(body) >= 5 and body[0] == 0xaa and int.from_bytes(body[1:5], 'big') == len(body):
        envelope_hint = 'AA_LENGTH_EXACT'
    elif len(body) >= 4 and int.from_bytes(body[:4], 'big') in (len(body), len(body) - 4):
        envelope_hint = 'BE_LENGTH_PLAUSIBLE'
    else:
        envelope_hint = 'UNKNOWN_OR_OPAQUE'
    # No raw data, hashes, prefix bytes, sequence values, account content,
    # arbitrary strings, decompressed content or IP addresses leave memory.
    return {'route_type': '0x4013', 'frame_bytes': len(frame),
            'header_bytes': hlen, 'body_bytes': size,
            'body_envelope_hint': envelope_hint,
            **_classify_method(body),
            'conclusion': 'STRUCTURAL_HINT_ONLY_NOT_AUTH_OR_RPC_PROOF'}
