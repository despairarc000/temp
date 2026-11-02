"""R076: privacy-safe CTDir literal equality, purely offline, no network.

Compares a transient complete 131-byte SYN against the exact ten-byte route
literal in SHA-pinned original owner-private Apollo. Returns a *fixed label*,
never the original static literal or actual phone route. No ACK permission.
A match does not establish which runtime object sent the SYN.
"""
from __future__ import annotations

import hashlib
import hmac
import struct
from pathlib import Path

from r057_original_address_callers import ORIGINAL_SHA, ORIGINAL_SIZE
from r058_name_service_wiring import progbits_sections, virtual_file_offset
from r075_directory_connector_discriminator import (
    ROUTE_LITERAL_LOAD, ROUTE_PC_ADD, route_literal_shape,
)
from r056_second_service_syn import first_syn_decision
from second_service_syn_gate import _parts
from rx_envelope import FrameError


def _original_route_name(private_apollo_path):
    """Private bytes live only in process memory; no exports or logs."""
    f = Path(private_apollo_path)
    if f.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("private Apollo original size mismatch")
    raw = f.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("private Apollo source hash mismatch")
    sections = progbits_sections(raw)
    if route_literal_shape(raw, sections)["route_literal_ascii_length"] != 10:
        raise ValueError("original directory route shape mismatch")
    ldr = ROUTE_LITERAL_LOAD
    off = virtual_file_offset(sections, ldr, 2)
    imm = struct.unpack_from("<H", raw, off)[0] & 0xff
    literal_address = ((ldr + 4) & ~3) + 4 * imm
    delta = struct.unpack_from(
        "<I", raw, virtual_file_offset(sections, literal_address, 4))[0]
    private_addr = (delta + ROUTE_PC_ADD + 4) & 0xffffffff
    start = virtual_file_offset(sections, private_addr, 11)
    return bytes(raw[start:start+10])


def classify_transient_frame(candidate, private_name):
    """Two transient byte strings in, one fixed label out; no values returned."""
    try:
        if type(candidate) is not bytes or type(private_name) is not bytes:
            return "REFUSED"
        if len(private_name) != 10 or len(candidate) != 131:
            return "REFUSED"
        if first_syn_decision(candidate)[0] != "TEN_BYTE_NAMED_ROUTE_CANDIDATE":
            return "REFUSED"
        _, _, _, _, observed_name = _parts(candidate)
        if len(observed_name) != 10:
            return "REFUSED"
        # Byte equality alone cannot identify connector ownership.
        return ("CTDIR_STATIC_ROUTE_MATCH" if
                hmac.compare_digest(observed_name, private_name)
                else "CTDIR_STATIC_ROUTE_DIFFERENT")
    except (ValueError, TypeError, FrameError, IndexError, OverflowError,
            StopIteration):
        return "REFUSED"


def classify_against_original(candidate, original_file):
    """Refuses absent/unpinned originals; source bytes never serialized."""
    try:
        return classify_transient_frame(
            candidate, _original_route_name(original_file))
    except (OSError, ValueError, struct.error):
        return "REFUSED"


# For later *opt-in* owner-local diagnostics; do not attach this comparison
# to ACK decisions or auto-start any listener.
