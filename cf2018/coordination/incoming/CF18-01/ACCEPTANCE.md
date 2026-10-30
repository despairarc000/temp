# CF18-01 prefix-model audit acceptance

Scope: inspect the limits of the existing hypothesis model, not implement an
unverified native parser. Defined before the audit tests on 2026-10-30.

- Pin the exact main commit and existing model blob; run only offline synthetic
  inputs, with no game files, network listener, ACK construction or device test.
- Exhaust the 16-bit input domain to identify the model's accepted two-byte word.
  Reversed prefix and every other two-byte value are negative controls.
- Demonstrate that empty/one-byte input fails, but a prefix alone succeeds.
- Demonstrate suffix/size blindness by removing, extending and changing all bytes
  after the prefix. This must not be called a native length-field test: the exact
  native field offset, byte order and length convention remain unknown.
- Demonstrate the absence of stream state with split-prefix inputs and absence
  of a consumed-length/trailing-frame decision with coalesced synthetic input.
- Characterize the prefix-only mutator's short-input rejection and preservation
  of arbitrary suffix bytes without claiming the result is a valid frame.
- Run the baseline knowledge route, doctor and unit tests, then lane audit tests.
  Results are LOCAL_SYNTHETIC / SOURCE_AUDIT only. No G2 or Q-01 status promotion.

Failure modes: native access unavailable; assumed length layout; confusing
`passes` with protocol acceptance; interpreting local fragmentation behavior as
the native splitter's behavior; publishing proprietary bytes. Stop native claims
until the exact 2018 library, provenance and receive-path branch trace exist.
