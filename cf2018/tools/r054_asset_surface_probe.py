"""R054: bounded read-only Unity/asset surface probe for original CF2018.

Reports signatures and *offsets* of known resource-path tokens, never file contents.
A missing raw token is NOT evidence a Unity Resources asset is absent.
Source-only, stdlib, no network, no listener, no writes to game files.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

DEFAULT_LIMIT = 8 * 1024 * 1024
MAX_FILES = 16
NEEDLES = (
    b"Config/GlobalDef/GlobalGameDef",
    b"Config/GlobalDef/GlobalMapDef",
    b"GlobalGameDef",
    b"GlobalMapDef",
    b"AITrainGame",
)
KEEP_HITS = 8


def detect_signature(header: bytes, total_size: int) -> str:
    """Strong signature where possible; do not trust filename extensions."""
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png_magic"
    if header.startswith((b"PK\x03\x04", b"PK\x05\x06")):
        return "zip_magic"
    for sig in (b"UnityFS\x00", b"UnityWeb\x00", b"UnityRaw\x00", b"UnityArchive\x00"):
        if header.startswith(sig):
            return sig[:-1].decode("ascii") + "_magic"
    if header.startswith(b"\x7fELF"):
        return "elf_magic"
    if header.startswith(b"MZ"):
        return "pe_mz_magic"
    if len(header) >= 20:
        metadata_size, declared_size, version, data_offset = struct.unpack(">4I", header[:16])
        # Unity 4.x serialized-file header candidate, not an object parser.
        if (
            7 <= version <= 22
            and 20 <= metadata_size < 64 * 1024 * 1024
            and data_offset >= metadata_size
            and declared_size >= data_offset
            and declared_size <= 8 * 1024 * 1024 * 1024
            and header[16] in (0, 1)
        ):
            if declared_size == total_size:
                return "unity_serialized_header_consistent"
            return "unity_serialized_header_size_mismatch_or_split"
    return "unknown_header"


def probe_file(path: Path, max_scan: int = DEFAULT_LIMIT) -> dict:
    """Inspect at most max_scan bytes, without copying or mutating an input."""
    if max_scan <= 0 or max_scan > 256 * 1024 * 1024:
        raise ValueError("max_scan must be 1..268435456 bytes")
    size = path.stat().st_size
    hits = {key.decode("ascii"): [] for key in NEEDLES}
    longest = max(map(len, NEEDLES))
    carry = b""
    consumed = 0
    with path.open("rb") as handle:
        header = handle.read(128)
        handle.seek(0)
        kind = detect_signature(header, size)
        limit = min(size, max_scan)
        while consumed < limit:
            chunk = handle.read(min(65536, limit - consumed))
            if not chunk:
                break
            window = carry + chunk
            window_start = consumed - len(carry)
            for key in NEEDLES:
                positions = hits[key.decode("ascii")]
                cursor = 0
                while len(positions) < KEEP_HITS:
                    hit = window.find(key, cursor)
                    if hit == -1:
                        break
                    offset = window_start + hit
                    if offset + len(key) > consumed and offset >= 0:
                        positions.append(offset)
                    cursor = hit + 1
            consumed += len(chunk)
            carry = window[-(longest - 1):]
    return {
        "file": path.name,
        "bytes": size,
        "kind": kind,
        "scan_bytes": consumed,
        "scan_complete": consumed == size,
        "literal_offsets": hits,
        "interpretation": "Raw-byte hints only; no Unity resource table or map-to-builder validation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Explicit local files only")
    parser.add_argument("--max-scan-mib", type=int, default=8,
                        help="Prefix scan budget per file (1-256 MiB, default 8)")
    args = parser.parse_args()
    if len(args.files) > MAX_FILES or not 1 <= args.max_scan_mib <= 256:
        parser.error("1-16 paths and 1-256 MiB per-file limit required")
    result = []
    for path in args.files:
        if not path.is_file():
            parser.error("missing regular file: " + str(path))
        result.append(probe_file(path, args.max_scan_mib * 1024 * 1024))
    print(json.dumps({"probe": "R054_source_only", "results": result}, indent=2))


if __name__ == "__main__":
    main()
