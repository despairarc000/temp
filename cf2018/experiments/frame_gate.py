"""First two-byte CF2018 Apollo receive-gate hypothesis.

Research-only: does NOT create or transmit a valid TGCP ACK.
Evidence: native Thumb receiver loads a little-endian 16-bit value and
compares it to 0x4366. This predicts incoming bytes 66 43.
The client-originated SYN instead began 43 66.
"""
from __future__ import annotations

EXPECTED_RECEIVE_WORD = 0x4366
CLIENT_TRANSMIT_PREFIX = bytes.fromhex("4366")
CANDIDATE_RECEIVE_PREFIX = bytes.fromhex("6643")


def first_native_gate(frame: bytes) -> dict[str, object]:
    """Model only the known 16-bit native RX compare, not full framing."""
    if len(frame) < 2:
        return {"passes": False, "reason": "too short"}
    word = int.from_bytes(frame[:2], "little")
    return {
        "passes": word == EXPECTED_RECEIVE_WORD,
        "received_le16": f"0x{word:04x}",
        "expected_le16": f"0x{EXPECTED_RECEIVE_WORD:04x}",
        "prefix_hex": frame[:2].hex(),
    }


def prefix_only_candidate(old_reply: bytes) -> bytes:
    """Create a *comparison fixture*; it is not a deployable server reply."""
    if not old_reply.startswith(CLIENT_TRANSMIT_PREFIX):
        raise ValueError("expected historical 43 66 prefix")
    if len(old_reply) < 7:
        raise ValueError("truncated input")
    return CANDIDATE_RECEIVE_PREFIX + old_reply[2:]


if __name__ == "__main__":
    print("old prefix:", first_native_gate(CLIENT_TRANSMIT_PREFIX))
    print("candidate prefix:", first_native_gate(CANDIDATE_RECEIVE_PREFIX))
    print("No network traffic or APK changes performed.")
