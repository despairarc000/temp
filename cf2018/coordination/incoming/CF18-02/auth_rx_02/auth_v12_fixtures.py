"""Synthetic CF2018 v1.2 0x2002 replies, reproduced independently, byte-for-byte.

Original new code; contains no authentic client account, token or UID.
Source of known SHA-256/length pins: exact v1.2 user-run Python generator.
DOES NOT contact a game, execute native code or prove authenticated state.
"""
import hashlib

AUTH_RESPONSE = 0x2002
EXPECTED = {
    "V11_EMPTY_ACCOUNT": {"length": 66, "sha256": "787fd8b6a013a1c469f065a8a6e269fa402968d6e2f503852411ab9e6d40d40e"},
    "V12_BODY_EMPTY": {"length": 49, "sha256": "527b6570d015c64355ab8d4d83c534dc3fe5975818485133a2c4b313edcbf4ca"},
    "V12_FULL_ZERO_ACCOUNT": {"length": 79, "sha256": "2aed3ae9a18a47497969bedad3332a2eb8a91aaf0e3a50839ace9843267199fa"},
}

def varuint(value):
    if not isinstance(value, int) or not 0 <= value < (1 << 64):
        raise ValueError("not an unsigned 64-bit value")
    result = bytearray()
    while value >= 128:
        result.append((value & 0x7f) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)

def nested(field_number, payload):
    return varuint((field_number << 4) | 5) + len(payload).to_bytes(4, "big") + payload

def scalar(field_number, value):
    return varuint((field_number << 4) | 1) + varuint(value)

def account_full_zero():
    return (varuint(0x10) + varuint(0) + varuint(0x21) + b"\x00"
            + nested(3, varuint(0x01) + b"\x00") + varuint(0x40) + varuint(0))

def reply(arm):
    if arm not in EXPECTED:
        raise ValueError("unsupported arm")
    if arm == "V12_BODY_EMPTY":
        auth = b""
    else:
        account = b"" if arm == "V11_EMPTY_ACCOUNT" else account_full_zero()
        auth = (nested(1, account) + varuint(0x20) + varuint(0)
                + nested(3, b"") + nested(4, b""))
    body = nested(AUTH_RESPONSE, auth)
    base = b"".join(scalar(k, value) for k, value in enumerate(
        (0x4366, 0, 1, 0x2002, 0, 0, 1, 0, len(body)), start=1))
    ext = varuint((AUTH_RESPONSE << 4) | 1) + b"\x00"
    header = nested(1, base) + nested(2, ext)
    result = b"\xaa" + (len(header) + 5).to_bytes(4, "big") + header + body
    expected = EXPECTED[arm]
    if len(result) != expected["length"]:
        raise AssertionError("fixture length drift")
    if hashlib.sha256(result).hexdigest() != expected["sha256"]:
        raise AssertionError("fixture hash drift")
    return result

def describe():
    for name in EXPECTED:
        value = reply(name)
        header = int.from_bytes(value[1:5], "big")
        yield {"name": name, "total": len(value), "header": header,
               "body": len(value) - header, "sha256": hashlib.sha256(value).hexdigest(),
               "wire_first_byte": value[0], "note": "SYNTHETIC - NOT VALIDATED"}

if __name__ == "__main__":
    for item in describe():
        print(item)
