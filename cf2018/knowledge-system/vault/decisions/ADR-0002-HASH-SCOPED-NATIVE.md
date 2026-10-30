# ADR-0002 — hash-scoped native evidence and offline framing

Date: 2026-10-30. Status: ADOPTED FOR OFFLINE ANALYSIS.

## Decision

Use the privately recovered v1.0.11.11 Mono mirror only with the pinned
[source receipt](../../../sources/SOURCE_PROVENANCE.md). Integrate its reviewed
[receiver trace](../research/ACK_RECEIVER.md), original offline framing subset
and source verifier. Keep original binaries and raw native output private.

The recovered GCloud path's decoded-marker comparison invalidates the historical
raw-prefix argument for that hash/path. Retain frame_gate.py solely as a historical
model; no prefix-only reply or A/B/C candidate follows from it. Parser base_type
is separate from effective extension type and never implies ACK acceptance.

## Consequences

Native lanes can continue bounded research when verified source is actually
available. CF18-G2-ACK-01 stays focused on body/session consumers and actual
negotiation. G0 phone/OBB equivalence and G2 client continuation remain unmet.
Synthetic parser tests, stubbed native controls and internal signature checks
retain their separate evidence classes. No device run is ready until runtime,
session/candidate and relay prerequisites exist. Original game files remain
unmodified; no live network experiments or bot implementation are introduced.

## Body/session integration refinement

The [continuation](../research/ACK_SESSION.md) keeps received timestamp data flow
separate from a server timestamp policy. Optional embedded-body syntax does not
establish a fast-auth path; a parser-stubbed account copy/state 4 never counts as
login. Canonical native controls stay opt-in by explicit private-source path,
with hash/ISA/budget guards and all send boundaries suppressed.
