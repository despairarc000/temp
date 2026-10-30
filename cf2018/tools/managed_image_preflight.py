"""Read-only managed-image header preflight, not Mono/IL or integrity acceptance.

No extraction, patching, decryption, repackaging, installation or networking.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

LIMIT = 16*1024*1024


def inspect_image(data):
    if type(data) is not bytes or not 0 < len(data) <= LIMIT:
        raise ValueError('image must be 1..16MiB')
    report = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'mz': data[:2] == b'MZ', 'status': 'STORED_NON_PE',
              'runtime_load_verified': False}
    if not report['mz']:
        return report
    def u16(off): return struct.unpack_from('<H', data, off)[0]
    def u32(off): return struct.unpack_from('<I', data, off)[0]
    def bounds(off, size):
        if off < 0 or size < 0 or off+size > len(data):
            raise ValueError('declared range outside file')
    try:
        bounds(0, 64)
        pe = u32(60)
        bounds(pe, 24)
        if data[pe:pe+4] != b'PE\0\0':
            raise ValueError('missing PE signature')
        count, optsize = u16(pe+6), u16(pe+20)
        if not 1 <= count <= 96:
            raise ValueError('invalid section count')
        opt = pe+24
        bounds(opt, optsize)
        magic = u16(opt)
        if magic not in (0x10b, 0x20b):
            raise ValueError('unsupported PE optional header')
        directory = opt+(96 if magic == 0x10b else 112)
        if directory+15*8 > opt+optsize:
            raise ValueError('missing CLI directory')
        if u32(directory-4) < 15:
            raise ValueError('CLI directory not declared')
        cli_rva, cli_size = u32(directory+14*8), u32(directory+14*8+4)
        if not cli_rva or cli_size < 72:
            raise ValueError('missing CLI header')
        sections = []
        sec = opt+optsize
        bounds(sec, count*40)
        for off in range(sec, sec+count*40, 40):
            rva, rawsize, raw = u32(off+12), u32(off+16), u32(off+20)
            bounds(raw, rawsize)
            sections.append((rva, rawsize, raw))
        def mapped(rva, size):
            for va, rawsize, raw in sections:
                if va <= rva and rva+size <= va+rawsize:
                    bounds(raw+rva-va, size)
                    return raw+rva-va
            raise ValueError('RVA not backed by section bytes')
        cli = mapped(cli_rva, 72)
        if u32(cli) < 72:
            raise ValueError('CLI cb too short')
        meta_rva, meta_size = u32(cli+8), u32(cli+12)
        if meta_size < 20:
            raise ValueError('metadata root too short')
        meta = mapped(meta_rva, meta_size)
        if data[meta:meta+4] != b'BSJB':
            raise ValueError('missing CLI metadata signature')
        version_size = u32(meta+12)
        header = meta+((16+version_size+3)&~3)
        if header+4 > meta+meta_size:
            raise ValueError('metadata version outside root')
        streams = u16(header+2)
        if not 1 <= streams <= 64:
            raise ValueError('invalid stream count')
        cursor, names = header+4, []
        for _ in range(streams):
            if cursor+8 > meta+meta_size:
                raise ValueError('truncated stream header')
            offset, size = u32(cursor), u32(cursor+4)
            start = cursor+8
            end = data.find(b'\0', start, min(start+32, meta+meta_size))
            if end < 0:
                raise ValueError('unterminated stream name')
            name = data[start:end].decode('ascii')
            if offset+size > meta_size:
                raise ValueError('stream outside metadata root')
            names.append(name)
            cursor = meta+((end+1-meta+3)&~3)
        if len(set(names)) != len(names) or not any(n in names for n in ('#~', '#-')):
            raise ValueError('missing/duplicate metadata table stream')
        report.update(status='MANAGED_HEADERS_PRESENT', cli_flags=u32(cli+16),
                      strong_name_size=u32(cli+36), metadata_streams=names)
    except (ValueError, struct.error, UnicodeDecodeError) as exc:
        report.update(status='MALFORMED_MANAGED_HEADERS', reason=str(exc))
    return report


def compare_bytes(original, candidate):
    if any(type(b) is not bytes or not 0 < len(b) <= LIMIT for b in (original, candidate)):
        raise ValueError('bounded byte images required')
    count, first, last = 0, None, None
    for i, (a, b) in enumerate(zip(original, candidate)):
        if a != b:
            count += 1
            first = i if first is None else first
            last = i
    if len(original) != len(candidate):
        start, end = min(len(original), len(candidate)), max(len(original), len(candidate))
        count += end-start
        first = start if first is None else first
        last = end-1
    return {'identical': original == candidate, 'size_delta': len(candidate)-len(original),
            'changed_positions': count, 'first_changed': first, 'last_changed': last,
            'candidate': inspect_image(candidate)}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('image', nargs='?')
    p.add_argument('--compare')
    a = p.parse_args()
    if not a.image:
        print('Inactive: supply an explicit private image path for read-only inspection.')
    else:
        def read(path):
            f = Path(path)
            if not 0 < f.stat().st_size <= LIMIT:
                raise ValueError('image outside size budget')
            return f.read_bytes()
        first = read(a.image)
        print(json.dumps(compare_bytes(first, read(a.compare)) if a.compare else inspect_image(first), indent=2))
