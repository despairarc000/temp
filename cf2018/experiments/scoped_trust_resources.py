"""Append isolated Android resources and one binary-manifest attribute.

No bytecode/native/asset rewriting. Callers must separately verify all original
resource values, original ZIP payload hashes and signatures before using output.
"""
import struct

U32 = lambda b, p: struct.unpack_from('<I', b, p)[0]
U16 = lambda b, p: struct.unpack_from('<H', b, p)[0]
NONE = 0xffffffff


def chunk(kind, header, body):
    return struct.pack('<HHI', kind, 8 + len(header), 8 + len(header) + len(body)) + header + body


def chunks(raw, start):
    p = start
    while p < len(raw):
        if p + 8 > len(raw):
            raise ValueError('truncated chunk header')
        kind, head, size = struct.unpack_from('<HHI', raw, p)
        if not 8 <= head <= size or p + size > len(raw):
            raise ValueError('invalid chunk bounds')
        yield p, kind, raw[p:p + size]
        p += size
    if p != len(raw):
        raise ValueError('chunk boundary')


def pool_values(raw):
    if U16(raw, 0) != 1 or U16(raw, 2) != 28:
        raise ValueError('unsupported string pool')
    count, styles, flags, begin, style_begin = struct.unpack_from('<5I', raw, 8)
    def length(p, utf8):
        x = raw[p] if utf8 else U16(raw, p)
        step, mask = (1, 0x80) if utf8 else (2, 0x8000)
        p += step
        if x & mask:
            x = ((x & (mask - 1)) << (8 if utf8 else 16)) | (raw[p] if utf8 else U16(raw, p))
            p += step
        return x, p
    values = []
    for i in range(count):
        p = begin + U32(raw, 28 + 4 * i)
        size, p = length(p, bool(flags & 0x100))
        if flags & 0x100:
            size, p = length(p, True)
            values.append(raw[p:p + size].decode('utf8'))
        else:
            values.append(raw[p:p + 2 * size].decode('utf-16le', errors='surrogatepass'))
    offsets = raw[28 + 4 * count:28 + 4 * (count + styles)]
    style_data = raw[style_begin:] if style_begin else b''
    return values, offsets, style_data, flags


def make_pool(values, style_offsets=b'', style_data=b'', flags=0):
    data, offsets = bytearray(), []
    for text in values:
        encoded = text.encode('utf-16le', errors='surrogatepass')
        n = len(encoded) // 2
        offsets.append(len(data))
        data += struct.pack('<H', n) if n < 0x8000 else struct.pack('<HH', 0x8000 | (n >> 16), n & 0xffff)
        data += encoded + b'\0\0'
    data += b'\0' * (-len(data) % 4)
    begin = 28 + 4 * len(values) + len(style_offsets)
    header = struct.pack('<5I', len(values), len(style_offsets) // 4, flags & ~0x101,
                         begin, begin + len(data) if style_data else 0)
    return chunk(1, header, b''.join(struct.pack('<I', o) for o in offsets) + style_offsets + data + style_data)


def extend_pool(raw, additions):
    values, offsets, styles, flags = pool_values(raw)
    return make_pool(values + additions, offsets, styles, flags), len(values)


def append_resources(raw):
    if U16(raw, 0) != 2 or U32(raw, 8) != 1 or U32(raw, 4) != len(raw):
        raise ValueError('single exact resource package required')
    parts = list(chunks(raw, U16(raw, 2)))
    if [kind for _, kind, _ in parts] != [1, 0x200]:
        raise ValueError('unexpected resource top-level chunks')
    global_pool, string_index = extend_pool(parts[0][2], ['res/xml/cf18_scoped_trust.xml', 'res/raw/cf18_local_ca.pem'])
    package = parts[1][2]
    head = U16(package, 2)
    if head != 288 or U32(package, 8) != 0x7f or U32(package, 284):
        raise ValueError('unsupported package identity/offset')
    type_at, key_at = U32(package, 268), U32(package, 276)
    sub = list(chunks(package, head))
    type_raw = next(c for p, _, c in sub if p == type_at)
    key_raw = next(c for p, _, c in sub if p == key_at)
    names = pool_values(type_raw)[0]
    if 'cf18trustxml' in names or 'cf18trustcert' in names or len(names) > 252:
        raise ValueError('resource type collision/budget')
    new_types, type_index = extend_pool(type_raw, ['cf18trustxml', 'cf18trustcert'])
    new_keys, key_index = extend_pool(key_raw, ['cf18_scoped_trust', 'cf18_local_ca'])
    result, offsets = bytearray(), {}
    for p, _, c in sub:
        offsets[p] = head + len(result)
        result += new_types if p == type_at else new_keys if p == key_at else c
    ids = []
    for i in range(2):
        tid = type_index + i + 1
        ids.append(0x7f000000 | tid << 16)
        # One default configuration and one file entry in each new custom type.
        result += chunk(0x202, struct.pack('<BBHI', tid, 0, 0, 1), struct.pack('<I', 0))
        config = struct.pack('<I', 64) + bytes(60)
        header = struct.pack('<BBHII', tid, 0, 0, 1, 8 + 12 + len(config) + 4) + config
        entry = struct.pack('<HHI', 8, 0, key_index + i) + struct.pack('<HBBI', 8, 0, 3, string_index + i)
        result += chunk(0x201, header, struct.pack('<I', 0) + entry)
    ph = bytearray(package[:head])
    struct.pack_into('<I', ph, 4, head + len(result))
    struct.pack_into('<I', ph, 268, offsets[type_at])
    struct.pack_into('<I', ph, 276, offsets[key_at])
    # All original IDs and type-entry chunks remain intact.
    out = chunk(2, struct.pack('<I', 1), global_pool + ph + result)
    return out, ids[0], ids[1]


def manifest_reference(raw, xml_id):
    if U16(raw, 0) != 3 or U32(raw, 4) != len(raw):
        raise ValueError('binary manifest required')
    parts = list(chunks(raw, U16(raw, 2)))
    pools = [c for _, k, c in parts if k == 1]
    if len(pools) != 1:
        raise ValueError('manifest string pool count')
    values = pool_values(pools[0])[0]
    if 'networkSecurityConfig' in values:
        raise ValueError('existing trust configuration requires review')
    new_pool, index = extend_pool(pools[0], ['networkSecurityConfig'])
    android = values.index('http://schemas.android.com/apk/res/android')
    output, modified, maps = [], 0, 0
    for _, kind, c in parts:
        if kind == 1:
            c = new_pool
        elif kind == 0x180:
            ids = list(struct.unpack('<' + 'I' * ((len(c) - 8) // 4), c[8:]))
            ids += [0] * (index + 1 - len(ids))
            ids[index] = 0x01010527  # framework android:networkSecurityConfig
            c = chunk(kind, b'', struct.pack('<' + 'I' * len(ids), *ids))
            maps += 1
        elif kind == 0x102 and values[U32(c, 20)] == 'application':
            start, size, count = struct.unpack_from('<HHH', c, 24)
            if size != 20:
                raise ValueError('manifest attribute layout')
            end = 16 + start + size * count
            attribute = struct.pack('<IIIHBBI', android, index, NONE, 8, 0, 1, xml_id)
            c = bytearray(c[:end] + attribute + c[end:])
            struct.pack_into('<I', c, 4, len(c))
            struct.pack_into('<H', c, 28, count + 1)
            modified += 1
        output.append(c)
    if modified != 1 or maps != 1:
        raise ValueError('manifest application/resource-map count')
    return chunk(3, b'', b''.join(output))


def trust_xml(hosts, certificate_id):
    import re
    if not hosts or len(hosts) > 8 or any(not re.fullmatch(r'[a-z0-9.-]+\.[a-z]{2,}', h) for h in hosts):
        raise ValueError('bounded original SDK DNS hosts required')
    strings = ['network-security-config', 'base-config', 'trust-anchors', 'certificates',
               'src', 'system', 'domain-config', 'domain', 'includeSubdomains', 'false'] + list(hosts)
    ix = {s: i for i, s in enumerate(strings)}
    data = bytearray(make_pool(strings))
    def node(kind, body):
        data.extend(chunk(kind, struct.pack('<II', 1, NONE), body))
    def start(name, attributes=()):
        attrs = b''.join(struct.pack('<IIIHBBI', NONE, ix[key], ix[value] if typ == 3 else NONE,
                                    8, 0, typ, ix[value] if typ == 3 else value) for key, typ, value in attributes)
        node(0x102, struct.pack('<IIHHHHHH', NONE, ix[name], 20, 20, len(attributes), 0, 0, 0) + attrs)
    def end(name):
        node(0x103, struct.pack('<II', NONE, ix[name]))
    start('network-security-config');start('base-config');start('trust-anchors')
    start('certificates', [('src', 3, 'system')]);end('certificates')
    end('trust-anchors');end('base-config');start('domain-config')
    for host in hosts:
        start('domain', [('includeSubdomains', 0x12, 0)])
        node(0x104, struct.pack('<IHBBI', ix[host], 8, 0, 3, ix[host]))
        end('domain')
    start('trust-anchors');start('certificates', [('src', 1, certificate_id)]);end('certificates')
    end('trust-anchors');end('domain-config');end('network-security-config')
    return chunk(3, b'', data)
