"""Read-only, privacy-preserving constraints on a routed application body.

A small apparent BE32 name length is *only a classification*, NOT evidence
that a native RPC name follows, nor evidence of plaintext, encryption or login.
No output includes packet bytes, raw integers, routes or private identifiers.
"""
from routed_body_diagnostic import diagnose_body, header_reason


def fixed_classes(body, sequence):
    if type(body) is not bytes or not 0 <= len(body) <= 8192:
        raise ValueError('bounded bytes required')
    if type(sequence) is not int or not 0 <= sequence < 2**32:
        raise ValueError('validated uint32 packet sequence required')
    base = diagnose_body(body, sequence)
    if len(body) < 8:
        status = 'SHORT'
    else:
        word = int.from_bytes(body[4:8], 'big')
        status = 'SMALL_BE32_1_TO_64' if 1 <= word <= 64 else 'OTHER'
    return {
        'sequence_prefix': base['sequence_prefix'],
        'word_after_sequence': status,
        'header_after_sequence_word': header_reason(body, 8),
        'original_after_sequence': base['legacy_after_sequence'],
        'interpretation': 'STRUCTURAL_CLASSIFICATION_NOT_NATIVE_PRODUCER',
    }
