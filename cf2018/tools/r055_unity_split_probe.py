"""R055: inspect a logical Unity Android file split into .split0, .split1, ...

Input is an EXPLICIT on-disk split0 path. Read-only; no temp concatenation,
network traffic, patching or proprietary byte output. Results are signatures
and literal-offset hints, not proof that a Resources asset exists or loads.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from r054_asset_surface_probe import (
    DEFAULT_LIMIT, KEEP_HITS, NEEDLES, detect_signature,
)

MAX_PARTS = 64
CHUNK = 65536


def find_parts(split0: Path) -> list[Path]:
    """Require a contiguous, nonempty .split0..N family in one directory."""
    if not split0.name.endswith(".split0"):
        raise ValueError("pass an exact .split0 filename")
    if not split0.is_file():
        raise ValueError("split0 file missing")
    prefix = split0.name[:-1]
    candidates = list(split0.parent.glob(prefix + "*"))
    indexed = {}
    for candidate in candidates:
        if not candidate.is_file():
            continue
        suffix = candidate.name[len(prefix):]
        if not suffix.isascii() or not suffix.isdecimal():
            continue
        # Reject .split00 aliases and other noncanonical names.
        if str(int(suffix)) != suffix:
            raise ValueError("noncanonical split index")
        index = int(suffix)
        if index >= MAX_PARTS or index in indexed:
            raise ValueError("too many parts or duplicate split index")
        indexed[index] = candidate
    if not indexed or 0 not in indexed:
        raise ValueError("no split0 found")
    expected = set(range(max(indexed) + 1))
    if set(indexed) != expected:
        raise ValueError("gap in split part family")
    paths = [indexed[i] for i in range(len(indexed))]
    if any(p.stat().st_size <= 0 for p in paths):
        raise ValueError("zero-size split part")
    return paths


def probe_split(split0: Path, max_scan: int = DEFAULT_LIMIT) -> dict:
    if max_scan <= 0 or max_scan > 256 * 1024 * 1024:
        raise ValueError("scan budget must be 1..256 MiB")
    parts = find_parts(split0)
    lengths = [p.stat().st_size for p in parts]
    logical_size = sum(lengths)
    hits = {k.decode("ascii"): [] for k in NEEDLES}
    carried = b""
    consumed = 0
    header = bytearray()
    longest = max(len(k) for k in NEEDLES)
    budget = min(logical_size, max_scan)
    for part in parts:
        if consumed >= budget:
            break
        with part.open("rb") as handle:
            while consumed < budget:
                block = handle.read(min(CHUNK, budget - consumed))
                if not block:
                    break
                if len(header) < 128:
                    header.extend(block[:128 - len(header)])
                window = carried + block
                window_start = consumed - len(carried)
                for key in NEEDLES:
                    offsets = hits[key.decode("ascii")]
                    pos = 0
                    while len(offsets) < KEEP_HITS:
                        at = window.find(key, pos)
                        if at < 0:
                            break
                        absolute = window_start + at
                        if absolute + len(key) > consumed and absolute >= 0:
                            offsets.append(absolute)
                        pos = at + 1
                consumed += len(block)
                carried = window[-(longest - 1):]
    return {
        "logical_name": split0.name.removesuffix(".split0"),
        "part_count": len(parts),
        "part_sizes": lengths,
        "logical_size": logical_size,
        "format_hint": detect_signature(bytes(header), logical_size),
        "scan_bytes": consumed,
        "scan_complete": consumed == logical_size,
        "literal_offsets": hits,
        "evidence_class": "read-only source-byte preflight, NOT parsed game config",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split0", type=Path, help="A specific original .split0 file")
    parser.add_argument("--max-scan-mib", type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.max_scan_mib <= 256:
        parser.error("max-scan-mib must be 1..256")
    try:
        result = probe_split(args.split0, args.max_scan_mib * 1024 * 1024)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({"probe": "R055_unity_split", "result": result}, indent=2))


if __name__ == "__main__":
    main()
