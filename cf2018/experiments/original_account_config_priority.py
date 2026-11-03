"""Exact-original APK config precedence audit with synthetic map inputs.

Interprets one bounded DEX method, not Android/Java or a live SDK. No account,
endpoint, original instruction body, database or configuration values exported.
"""
import hashlib, io
from pathlib import Path
from zipfile import ZipFile
from original_account_sdk_chain import APK_SHA


def original_method(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != APK_SHA:
        raise ValueError('exact original APK required')
    from loguru import logger
    logger.disable('androguard')
    from androguard.core.dex import DEX
    with ZipFile(io.BytesIO(raw)) as archive:
        dex = DEX(archive.read('classes.dex'))
    cls = dex.get_class('Lcom/tencent/imsdk/android/base/config/IMSDKConfigManager;')
    methods = [m for m in cls.get_methods() if m.get_name() == 'getOrDefault']
    if len(methods) != 1:
        raise ValueError('original config selector changed')
    method = methods[0]
    if method.get_code().get_registers_size() != 5 or method.get_code().get_ins_size() != 3:
        raise ValueError('original selector registers changed')
    return method


def evaluate(method, user, downloaded, key='synthetic_setting', default='SYNTHETIC_DEFAULT'):
    """Source-op interpretation on synthetic maps only; never invoke the APK."""
    instructions = dict(method.get_instructions_idx())
    registers = {2: {'mUserConfigCache': user, 'mConfigCache': downloaded}, 3: key, 4: default}
    pc = 0
    result = None
    for _ in range(48):
        if pc not in instructions:
            raise ValueError('selector instruction boundary')
        ins = instructions[pc]
        op, args = ins.get_name(), ins.get_operands()
        next_pc = pc + ins.get_length()
        if op == 'move-object':
            registers[args[0][1]] = registers[args[1][1]]
        elif op == 'iget-object':
            name = args[-1][-1].split('->')[1].split()[0]
            if name not in ('mUserConfigCache', 'mConfigCache'):
                raise ValueError('unexpected selector field')
            registers[args[0][1]] = registers[args[1][1]][name]
        elif op == 'if-eqz':
            value = registers[args[0][1]]
            # DEX object null differs from an empty but non-null Java Map.
            if value is None or (isinstance(value, (int, bool)) and value == 0):
                next_pc = pc + 2 * args[-1][1]
        elif op == 'invoke-interface':
            target = args[-1][-1]
            obj, name = registers[args[0][1]], registers[args[1][1]]
            if target == 'Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z':
                result = name in obj
            elif target == 'Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;':
                result = obj.get(name)
            else:
                raise ValueError('unexpected selector call')
        elif op in ('move-result', 'move-result-object'):
            registers[args[0][1]] = result
        elif op == 'check-cast':
            value = registers[args[0][1]]
            if args[-1][-1] != 'Ljava/lang/String;' or (value is not None and not isinstance(value, str)):
                raise ValueError('unexpected selector cast')
        elif op == 'return-object':
            return registers[args[0][1]]
        elif op == 'goto':
            next_pc = pc + 2 * args[-1][1]
        else:
            raise ValueError('unsupported selector instruction')
        pc = next_pc
    raise ValueError('selector instruction budget')
