"""R074: observer-only classifier for named-route + unit-ID-field delta.

Takes two transient complete client SYN frames; never writes packets, file
contents, raw field values, routes, accounts, or permits an ACK. An
information-only match is not server authentication/session proof.
"""
from r056_second_service_syn import first_syn_decision
from second_service_syn_gate import _parts, compare_security_context
from rx_envelope import FrameError


def route_unit_context_label(candidate, reference):
    """Return a fixed privacy-safe label; never serialize any input values."""
    refused = "REFUSED"
    try:
        if type(candidate) is not bytes or type(reference) is not bytes:
            return refused
        if len(reference) != 133 or len(candidate) != 131:
            return refused
        if first_syn_decision(reference)[0] != "REFERENCE_NAMED_ROUTE_CANDIDATE":
            return refused
        if first_syn_decision(candidate)[0] != "TEN_BYTE_NAMED_ROUTE_CANDIDATE":
            return refused
        if compare_security_context(candidate, reference) == "MATCH_EXCEPT_ROUTE":
            return "ROUTE_ONLY_MATCH"
        base_a, ext_a, syn_a, route_a, name_a = _parts(reference)
        base_b, ext_b, syn_b, route_b, name_b = _parts(candidate)
        if len(name_a) != 12 or len(name_b) != 10:
            return refused
        if route_a[4] != route_b[4]:
            return refused
        if base_a[0][3] != base_b[0][3]:
            return refused
        if [f[4] for f in base_a] != [f[4] for f in base_b]:
            return refused
        if ext_a[0][4] != ext_b[0][4]:
            return refused
        if [(x[0], x[1], x[4]) for x in syn_a] != [
            (y[0], y[1], y[4]) for y in syn_b
        ]:
            return refused
        left, right = {x[0]: x for x in syn_a}, {x[0]: x for x in syn_b}
        if 5 not in left or 5 not in right:
            return refused
        if left[5][1] != 0 or right[5][1] != 0:
            return refused
        if left[5][2] == right[5][2]:
            return refused
        # Same encoded field length; other fields must be exact-byte equal.
        if len(left[5][3]) != len(right[5][3]):
            return refused
        if any(left[n][3] != right[n][3] for n in left if n not in (5, 14)):
            return refused
        return "ROUTE_AND_UNIT_FIELD5_ONLY"
    except (ValueError, FrameError, TypeError, IndexError, StopIteration,
            OverflowError, KeyError):
        return refused


# The label is informational only. No server ACK, session or policy gate API.
