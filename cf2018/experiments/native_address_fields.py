"""Original generated AddressService serialization/decoding, synthetic memory only."""
from native_control import NativeControl, AUX, BUF, STOP


def query_args(library, *, service_size=9, game_id=1, unit_id=2):
    if type(service_size) is not int or not 0 <= service_size <= 32:
        raise ValueError('bounded independent synthetic service size required')
    if any(type(v) is not int or not 0 <= v < 2**64 for v in (game_id, unit_id)):
        raise ValueError('independent unsigned64 values required')
    n = NativeControl(library)
    protocol, request, args, name = AUX+0x100, AUX+0x400, AUX+0x500, BUF+0x100
    n.write(protocol, 0x4f4768)  # original binary protocol vtable +8
    n.write(protocol+0x10, 16)  # explicit recursion budget
    n.write(protocol+0x14, AUX+0x300)
    n.write(request+8, game_id, 8)
    n.write(request+16, unit_id, 8)
    n.write(request+24, name)
    n.write(name-12, service_size)
    if service_size:
        n.uc.mem_write(name, b'A'*service_size)
    n.write(args+4, request)
    chunks = []
    def sink(transport, pointer, count, unused):
        if transport != AUX+0x300 or count > 64 or sum(map(len, chunks))+count > 256:
            raise ValueError('synthetic output transport bounds')
        chunks.append(bytes(n.uc.mem_read(pointer, count)))
        return 0
    code = n.execute(0x39ed4c, (args, protocol), {
        0x398ede: ('bounded synthetic memory output; no socket', sink)})
    return {'return': code, 'wire': b''.join(chunks),
            'remaining_depth': n.read(protocol+12), 'stubs': n.calls}


def result_fields(library, wire):
    if type(wire) is not bytes or not 1 <= len(wire) <= 64:
        raise ValueError('independent synthetic result subset1..64 required')
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC
    n = NativeControl(library)
    protocol, result, response = AUX+0x100, AUX+0x400, AUX+0x500
    n.write(protocol, 0x4f4768)
    n.write(protocol+0x10, 16)
    n.write(protocol+0x14, AUX+0x300)
    n.write(result+4, response)
    n.write(response+8, AUX+0x780)
    position, failed = [0], []
    def source(transport, pointer, count, unused):
        if transport != AUX+0x300 or count > 64 or position[0]+count > len(wire):
            raise ValueError('synthetic input exhausted; not a native decoder return')
        n.uc.mem_write(pointer, wire[position[0]:position[0]+count])
        position[0] += count
        return count
    def empty_string(dest, source, unused, unused2):
        if bytes(n.uc.mem_read(source, 1)) != b'\0':
            raise ValueError('only static empty-name runtime assignment supported')
        n.write(dest, AUX+0x780)
        return dest
    def stop_at_exception(u, address, size, unused):
        if address in (0x39eaae, 0x39ead8):
            failed.append({'address': hex(address), 'predicate':
                           'required_result_absent' if address == 0x39eaae else
                           'required_reason_string_absent'})
            u.reg_write(UC_ARM_REG_R0, (-99) & 0xffffffff)
            u.reg_write(UC_ARM_REG_PC, STOP | 1)
    n.uc.hook_add(UC_HOOK_CODE, stop_at_exception)
    code = n.execute(0x39eebc, (result, protocol), {
        0x398df4: ('bounded synthetic memory input; no socket', source),
        0x3f8f7c: ('bounded static empty-string assignment runtime', empty_string),
        0x3f8a20: ('temporary string destruction no-op; no allocation', 0)})
    status = n.read(response+4)
    return {'native_return': None if failed else code,
            'stopped_before_exception_allocation': bool(failed),
            'failed_predicate': failed[0] if failed else None,
            'consumed': position[0], 'wrapper_presence': bool(n.read(result+8, 1) & 1),
            'result': status if status < 2**31 else status-2**32,
            'stubs': n.calls,
            'limits': 'generated result reader only; no pending map, endpoint or session acceptance'}
