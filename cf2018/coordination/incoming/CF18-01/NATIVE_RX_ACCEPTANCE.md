# CF18-01 native RX acceptance (defined before the public proposal)

Base: 925ecc3489b330dc9c6cf7738d6241450e4f24fe. Scope: the recovered
APKPure mirror's ARM32 GCloud splitter, not an accepted server ACK.

- Verify embedded package/version, APK signature and signed-entry digests; pin
  the actual library SHA-256 before interpreting addresses. Do not claim it is
  byte-identical to the historical phone package without that comparison.
- Establish the direct receive caller, header decoder and independent TX path.
  Distinguish decoded structure fields from raw socket bytes.
- Native controls must execute the fingerprinted Thumb code with independent
  synthetic inputs, a finite instruction/time budget, no network, and explicit
  stubs. Never stub the splitter, header decoder, varint decoder or comparison.
- Negative controls: both raw two-byte prefix orders; decoded swapped marker;
  short buffer; truncated declared header/body; malformed coalesced lookahead.
  Positive control: decoded correct marker in a synthetic TLV envelope.
- Public original parser is a deliberately strict AA/varint framing subset.
  It must bound memory/length/varints, preserve fragments and coalesced frames,
  and fail closed on unsupported fields/99 mode, duplicates and EOF truncation.
  Those policy choices are not claimed as native rejection rules.
- Parser success, native splitter return zero and signature validity are not
  proof of ACK/session acceptance, phone path selection or G2 advancement.
- Publish only original code, synthetic fixtures and descriptive provenance;
  no original binary, raw disassembly, decompilation or archive contents.

Failure modes: incorrect mirror identity; wrong overload or runtime path;
confusing little-endian decoded storage with wire order; incomplete DLL
provenance; unsupported native behavior hidden by emulator stubs; mistaking
strict parser policy for complete native parity. No device experiment is enabled.
