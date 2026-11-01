# R066: prepared native SYN state through ACK into auth-send boundary

2026-11-01 UTC. Original-native emulation with explicit stubs and synthetic input. No phone, network, client edits, actual auth-send, accepted login or gameplay.

The earlier ACK controls seeded decoded or empty connection state. This continuation first executes original `gcloud_tgcpapi_send_syn_msg` at0x3aba5c with synthetic named-route configuration at handle+0x3400/+0x3408, non-relay state, zeroed synthetic account/security fields, initialized handle and synthetic descriptor42. Original `tgcpapi_build_frame_base` executes. Name copy uses a bounded strncpy stub. Outgoing pack/encrypt/send at0x3ab430 is suppressed. Thus no original SYN bytes are serialized or sent by this control.

The native SYN preparer selects route-kind4 and copies the synthetic name into its outgoing SYN structure (kind at+0x2de1/name at+0x2de8), then stores transport state2 at0x3abc34. The complete prepared handle region is transferred into a fresh fingerprinted emulator context at identical addresses to avoid accumulated instrumentation hooks. This transfers data, not an Android connection or complete library runtime.

In that prepared state the original `OnStateKeySyning` (0x3a9f8c), gather, header decode, receive/decrypt and ACK decoder execute on a preloaded independent mode0/empty-body AA-framed ACK. Real native parsing reaches `gcloud_tgcpapi_send_authreq_msg` at0x3ab964; that call is suppressed with sentinel-77. No account/token construction executes. Memory/log wrappers and network no-new-data status are explicit stubs inherited from NativeControl. No cipher/DH success was simulated.

## Seven cases in three test methods

| Synthetic case | Observed result |
|---|---|
| 12-byte and 10-byte names | Both route-kind4/name-copy checks pass; same63-byte ACK consumed; auth-send boundary reached; state2 retained because auth send suppressed |
| Wrong decoded magic | -13, no auth-send |
| Effective unsupported key mode1 | -30, no auth-send |
| Extra raw4366 client-style prefix | -18, no auth-send |
| Truncated ACK | Return0/wait, no auth-send |
| Relay requested | SYN preparer does not construct named-route variant4; no claim about relay acceptance |

**3 original-gated test methods /7 cases PASS.** `NativeControl` independently requires exact Apollo size5243704/SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` and ARM ELF32 little-endian identity. Public CI skips these three tests without explicitly supplied private source/dependencies.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cf2018/private/analysis_deps CF18_APOLLO_LIBRARY=/absolute/path/to/original/libapollo.so python -m unittest discover -s cf2018/tests -p test_native_syn_ack_handoff.py -v
```

## Decision and missing evidence

In this bounded non-relay, mode0 synthetic configuration, named-route length alone does not prevent the existing ACK grammar from reaching auth-send. This narrows an explanation; it does not prove that the actual R037 phone connection has this same configuration, identify its service, validate server keys/session/timestamp, or justify automatic ACKs to arbitrary ten-byte routes. The R065 integrated handler remains HOLD_NO_ACK. Next compare exact non-route SYN/security fields against the already working reference in memory, preserving full-frame/session context, before preparing any narrowly scoped manual second-service ACK experiment. No repeated HOLD-only phone capture is needed.
