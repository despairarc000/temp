"""Original strict AA/varint offline framing subset for the fingerprinted mirror.

This layer checks framing only. It does not validate ACK/session/crypto semantics,
choose the phone's native path, create replies, connect, listen or alter files.
Unknown/duplicate fields and 99 mode are intentionally unsupported policy.
"""
from dataclasses import dataclass


class FrameError(ValueError):
    pass


@dataclass(frozen=True)
class Frame:
    header_size: int
    body: bytes
    base_type: int | None  # opaque extension may replace it in the native decoder


def _uint(data, position, end, bits):
    value = 0
    for shift in range(0, bits, 7):
        if position >= end:
            raise FrameError('truncated varint inside declared header')
        byte = data[position]
        position += 1
        value |= (byte & 127) << shift
        if value >= 1 << bits:
            raise FrameError('varint overflow')
        if not byte & 128:
            return value, position
    raise FrameError('varint overflow')


def _base(data, start, end):
    values = {}
    position = start
    while position < end:
        tag, position = _uint(data, position, end, 32)
        field = tag >> 4
        if field not in range(1, 10) or tag & 15 != 1:
            raise FrameError('unsupported base field/type')
        if field in values:
            raise FrameError('duplicate base field')
        if field == 6:
            if position >= end:
                raise FrameError('truncated uint8')
            value = data[position]
            position += 1
        else:
            value, position = _uint(data, position, end, 16 if field <= 4 else 32)
        values[field] = value
    if values.get(1) != 0x4366:
        raise FrameError('decoded base marker mismatch')
    if 9 not in values:
        raise FrameError('body length field required by strict proposal')
    return values


def _header(data, size):
    position = 5
    fields = set()
    base = None
    while position < size:
        tag, position = _uint(data, position, size, 32)
        if tag not in (0x15, 0x25):
            raise FrameError('unsupported header field/type')
        if tag in fields:
            raise FrameError('duplicate header field')
        fields.add(tag)
        if position + 4 > size:
            raise FrameError('truncated nested length')
        length = int.from_bytes(data[position:position + 4], 'big')
        position += 4
        end = position + length
        if end > size:
            raise FrameError('nested size exceeds header')
        if tag == 0x15:
            base = _base(data, position, end)
        # Extension bytes remain opaque; no extension/ACK acceptance is claimed.
        position = end
    if base is None:
        raise FrameError('base field required by strict proposal')
    return base


class Receiver:
    """One bounded stream; terminal failure requires a fresh Receiver.

    Default 64 KiB frame cap is a proposal resource policy, not a native constant.
    feed() input is at most that cap; the retained buffer is at most twice it.
    Native's 32-byte gather threshold/lookahead/error timing is not reproduced.
    """
    def __init__(self, max_frame=65536):
        if type(max_frame) is not int or not 32 <= max_frame <= 1048576:
            raise ValueError('frame cap must be an integer between 32 and 1048576')
        self.max_frame = max_frame
        self.buffer = bytearray()
        self.failed = False
        self.finished = False

    def feed(self, chunk):
        if self.failed:
            raise FrameError('receiver is failed')
        if self.finished:
            raise FrameError('receiver is finished')
        if not isinstance(chunk, bytes):
            raise TypeError('bytes required')
        try:
            if len(chunk) > self.max_frame or len(self.buffer) + len(chunk) > 2 * self.max_frame:
                raise FrameError('input budget exceeded')
            self.buffer.extend(chunk)
            frames = []
            while self.buffer:
                if self.buffer[0] != 0xaa:
                    raise FrameError('unsupported wire marker; AA subset only')
                if len(self.buffer) < 5:
                    break
                size = int.from_bytes(self.buffer[1:5], 'big')
                if not 5 <= size <= self.max_frame or size >= 1 << 31:
                    raise FrameError('declared header size outside policy')
                if len(self.buffer) < size:
                    break
                base = _header(self.buffer, size)
                total = size + base[9]
                if total > self.max_frame:
                    raise FrameError('declared frame size exceeds cap')
                if len(self.buffer) < total:
                    break
                frames.append(Frame(size, bytes(self.buffer[size:total]), base.get(4)))
                del self.buffer[:total]
            return frames
        except FrameError:
            self.failed = True
            self.buffer.clear()
            raise

    def finish(self):
        self.finished = True
        if self.failed or self.buffer:
            self.failed = True
            self.buffer.clear()
            raise FrameError('failed receiver or truncated final frame')
