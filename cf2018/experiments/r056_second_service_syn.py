"""CF2018 R056: fail-closed server-side classification of first TGCP SYN.

Read-only, source-only parser for the exact 2018 GCloud AA-framing subset.
It has no listener, writer or ACK generator; the existing reference-SYN handler
remains the only justified active handler. NEVER auto-ACK a 10-byte route.
"""
from rx_envelope import FrameError
from inbound_4013_reply_preflight import _fields

MAX_FIRST_FRAME = 1024
REFERENCE_ROUTE = b"QueryAddrSvr"


def first_syn_decision(wire):
    """Return privacy-safe fixed labels and a fail-closed handler disposition.

    Input: one *complete*, already-buffered, original-client first TCP frame,
    including the observed two-byte 43 66 preamble. This is not a streaming
    decoder. Neither a valid SYN nor a changed route proves authentication.
    """
    refused = ("UNRECOGNIZED_OR_INCOMPLETE_SYN", "NO_ACK")
    if type(wire) is not bytes or not 32 <= len(wire) <= MAX_FIRST_FRAME:
        return refused
    if not wire.startswith(b"\x43\x66\xaa"):
        return refused
    try:
        # Client TX uses kind0 varuint base fields except kind1 byte field6.
        # The inbound server-reply
        # Receiver requires kind1 and must NOT be applied to this boundary.
        declared = int.from_bytes(wire[3:7], 'big')
        if declared != len(wire) - 2:
            return refused
        outer = _fields(wire[7:])
        if set(outer) != {1, 2} or outer[1][0] != 5 or outer[2][0] != 5:
            return refused
        base = _fields(outer[1][1])
        if base.get(1) != (0, 0x4366) or base.get(9) != (0, 0):
            return refused
        if any(k not in range(1, 10) or v[0] != (1 if k == 6 else 0)
               for k, v in base.items()):
            return refused
        if 4 in base and base[4] != (0, 0x1001):
            return refused
        extension = _fields(outer[2][1])
        if set(extension) != {0x1001} or extension[0x1001][0] != 5:
            return refused
        syn = _fields(extension[0x1001][1])
        if 14 not in syn or syn[14][0] != 5:
            return refused
        route = _fields(syn[14][1])
        if set(route) != {4} or route[4][0] != 5:
            return refused
        named = _fields(route[4][1])
        if set(named) != {1} or named[1][0] != 5:
            return refused
        name = named[1][1]
        if not 1 <= len(name) <= 127:
            return refused
        if name == REFERENCE_ROUTE:
            # Still no independent source-bounded proof of the full original
            # reference SYN; pass to the preexisting strict byte-equality gate.
            return ("REFERENCE_NAMED_ROUTE_CANDIDATE",
                    "DEFER_TO_PINNED_REFERENCE_GATE")
        if len(name) == 10:
            # Phone R037 observed a different 10-byte name after a correlated
            # 0x4013 response. The ACK session/key policy is NOT verified.
            return ("TEN_BYTE_NAMED_ROUTE_CANDIDATE", "HOLD_NO_ACK")
        return ("OTHER_NAMED_ROUTE", "HOLD_NO_ACK")
    except (FrameError, ValueError, OverflowError, IndexError, TypeError):
        return refused

