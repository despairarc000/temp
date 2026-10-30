# Coordinator acceptance: hash-scoped native/source integration

Reviewed base c52243228e8d2d38dd6b4c1d85f464d9f94461f8, CF18-00, 2026-10-30.
Define these checks before editing canonical implementation:

- Independently verify all tracked snapshot blobs and rerun CF18-01/02/04 source
  controls against the actual pinned private APK/library. Keep every stub and
  evidence class explicit; no original or lane packet is copied into public code.
- Integrate only original AA/varint offline framing and private-source verifier.
  No listener, server ACK, crypto success, APK modification or phone test.
- Framing metadata must call the base field base_type, not effective message type:
  native extension union decoding can replace it. Opaque extension bytes cannot
  establish ACK acceptance. End-of-input must prevent reuse of that stream.
- Preserve negative controls for raw prefix orders, decoded marker, truncation,
  size mismatch, duplicates, caps, wrong identity/hash, signed-chain damage and
  invalid CMS. Add controls for base-vs-extension type and feed after EOF.
- Update source pointers, current findings, EVIDENCE/questions/WORKLOG, navigation,
  Graphify/ICM and decision records. Preserve historical reports as historical.
- Canonical tests + knowledge doctor must pass. Optional private tests must be
  explicitly selected and reported separately from a source-free run's skips.
- Keep G0 phone/OBB equivalence incomplete and G2 BLOCKED; no device A/B/C plan
  is ready without runtime path, candidate/session and relay prerequisites.
- After the substantive integration commit exists, record its exact SHA in the
  compact assignments handoff. Never fabricate a self-referential commit hash.
