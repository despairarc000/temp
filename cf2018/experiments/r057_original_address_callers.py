"""R057: exact-original CF2018 native AddressService caller provenance.

Read-only ELF32/Thumb-2 direct-BL audit. No network, no original bytes or
symbol dumps, no service names/route strings, no DLL/APK/OBB changes.
A direct call edge does NOT identify the caller executed by the phone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

ORIGINAL_SHA = "4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8"
ORIGINAL_SIZE = 5243704
ADDRESS_SERVICE_GET = 0x39D18C
RPC_INIT_LB_IP = 0x3C32CC
GCLOUD_ROUTE_SET = 0x3A33A0
RECV_ACK = 0x3AC0B8

EXPECTED = {
    ADDRESS_SERVICE_GET: {
        0x3A6890: "CDefaultNameService5Query",
        0x3C334E: "RpcConnector15InitLbIpAddress",
    },
    RPC_INIT_LB_IP: {
        0x3C474C: "RpcConnector4Init",
    },
    GCLOUD_ROUTE_SET: {
        0x3C6C4A: "CGCloudConnector13connectTConnd",
    },
    RECV_ACK: {
        0x3A845A: "gcloud_tgcpapi_start_connection",
        0x3A9FB0: "OnStateKeySyning",
    },
}


@dataclass(frozen=True)
class Section:
    type: int
    flags: int
    address: int
    offset: int
    size: int
    link: int
    entry_size: int


@dataclass(frozen=True)
class Func:
    address: int
    size: int
    name: str


def thumb_bl_target(h1: int, h2: int, site: int):
    """Decode only 32-bit Thumb BL, not BLX or non-BL instructions."""
    if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
        return None
    s = (h1 >> 10) & 1
    i1 = 1 ^ ((h2 >> 13) & 1) ^ s
    i2 = 1 ^ ((h2 >> 11) & 1) ^ s
    relative = ((s << 24) | (i1 << 23) | (i2 << 22)
                | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
    if s:
        relative -= 1 << 25
    return (site + 4 + relative) & 0xFFFFFFFF


def parse_elf(raw: bytes):
    """Minimal bounded ELF32LE/ARM section + function-symbol index."""
    if (len(raw) < 52 or raw[:6] != b"\x7fELF\x01\x01"
            or struct.unpack_from("<H", raw, 18)[0] != 40):
        raise ValueError("exact original ELF32LE ARM required")
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shent, shnum = struct.unpack_from("<HH", raw, 46)
    if shent < 40 or not 1 <= shnum <= 512 or shoff + shent * shnum > len(raw):
        raise ValueError("invalid section-header bounds")
    sections = []
    for i in range(shnum):
        p = shoff + i * shent
        _, kind, flags, addr, off, size, link, _, _, ent = struct.unpack_from("<10I", raw, p)
        if off > len(raw) or size > len(raw) - off:
            if kind != 8:  # NOBITS occupies no file bytes
                raise ValueError("section outside ELF")
        sections.append(Section(kind, flags, addr, off, size, link, ent))
    funcs = []
    for s in sections:
        if s.type not in (2, 11):
            continue
        if s.link >= len(sections) or not 16 <= s.entry_size <= 256:
            raise ValueError("bad symbol table")
        strings = sections[s.link]
        if s.size % s.entry_size:
            raise ValueError("misaligned symbols")
        for off in range(s.offset, s.offset + s.size, s.entry_size):
            name_off, addr, size = struct.unpack_from("<III", raw, off)
            sym_type = raw[off + 12] & 15
            if sym_type != 2 or not addr or not size or name_off >= strings.size:
                continue
            start = strings.offset + name_off
            end = raw.find(b"\0", start, strings.offset + strings.size)
            if end < 0 or end - start > 1024:
                raise ValueError("bad symbol name")
            name = raw[start:end].decode("utf-8", errors="replace")
            funcs.append(Func(addr & ~1, size, name))  # Thumb function values are odd.
    executable = tuple(s for s in sections if s.type == 1 and s.flags & 4)
    if not executable or not funcs:
        raise ValueError("executable code/functions absent")
    return executable, funcs


def direct_calls(raw: bytes, executable, targets):
    """Scan aligned executable bytes for direct Thumb BL to target addresses."""
    hits = {addr: set() for addr in targets}
    for s in executable:
        for offset in range(s.offset, s.offset + s.size - 3, 2):
            site = s.address + offset - s.offset
            dest = thumb_bl_target(*struct.unpack_from("<HH", raw, offset), site)
            if dest in hits:
                hits[dest].add(site)
    return hits


def containing_symbol(functions, site):
    options = [f for f in functions if f.address <= site < f.address + f.size]
    if not options:
        return None
    return min(options, key=lambda f: f.size).name


def callback_symbol_evidence(functions):
    """Symbol presence only; no virtual dispatch/runtime binding claim."""
    names = [f.name for f in functions]
    signals = {
        "default_nameservice_callback": "CDefaultNameService19OnGetServiceAddress",
        "tgcp_name_result_observer": "CTGcp17OnQueryNameResult",
        "name_service_bound_function_handler": "Function_handler",
    }
    found = {
        "default_nameservice_callback": any(signals["default_nameservice_callback"] in n for n in names),
        "tgcp_name_result_observer": any(signals["tgcp_name_result_observer"] in n for n in names),
        "name_service_bound_function_handler": any(
            signals["name_service_bound_function_handler"] in n and "CDefaultNameService" in n
            for n in names
        ),
    }
    return found


def audit(original):
    path = Path(original)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("incorrect original library size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("incorrect original library hash")
    executable, functions = parse_elf(raw)
    callers = direct_calls(raw, executable, EXPECTED)
    mismatches = []
    for target, expected in EXPECTED.items():
        if callers[target] != set(expected):
            mismatches.append("direct_callset_mismatch")
        for site, symbol_part in expected.items():
            if symbol_part not in (containing_symbol(functions, site) or ""):
                mismatches.append("caller_symbol_mismatch")
    if mismatches:
        raise ValueError("source call graph did not match pinned original")
    callback_symbols = callback_symbol_evidence(functions)
    if not all(callback_symbols.values()):
        raise ValueError("native callback symbol evidence missing")
    return {
        "evidence": "EXACT_ORIGINAL_NATIVE_STATIC_DIRECT_BL",
        "sha256_match": True,
        "address_service_direct_caller_count": len(callers[ADDRESS_SERVICE_GET]),
        "address_service_direct_callers": (
            "GCloud.CDefaultNameService.Query",
            "pebble.rpc.RpcConnector.InitLbIpAddress",
        ),
        "rpc_lb_init_is_called_by": "pebble.rpc.RpcConnector.Init",
        "independent_controls": "GCloud.CTGcp.SetRouteInfo + GCloud ACK receiver",
        "original_direct_edges_verified": sum(len(x) for x in EXPECTED.values()),
        "callback_symbols": callback_symbols,
        "virtual_callback_invocation": "NOT_EXECUTION_VERIFIED",
        "caller_selected_on_phone": "NOT_DETERMINED",
        "actual_ten_byte_route_name": "NOT_IDENTIFIED",
        "second_service_ack_session": "UNVERIFIED",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    args = p.parse_args()
    try:
        result = audit(args.original_lib)
    except (ValueError, OSError, struct.error):
        print(json.dumps({"status": "REFUSED", "reason": "SOURCE_OR_AUDIT_MISMATCH"}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
