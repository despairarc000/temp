> Native 99/bounds continuation: [CF18-G2-RX-02](BOUNDARY_RESULT.md).

# CF18-01 — prefix-model limitations audited

Date: 2026-10-30 UTC. State: SUBMITTED for coordinator review; native trace
BLOCKED_SOURCE. No active claim remains. Q-01 remains a hypothesis; G2 remains
blocked. This is SOURCE_AUDIT + LOCAL_SYNTHETIC evidence, not a native handoff.

## Baseline and provenance

- Exact main base: `91553f564dc502bd435571eb0beb63c2ebae516a`.
- Model: `cf2018/experiments/frame_gate.py`, Git blob
  `5e193bc0f3f347a3b3cf59a959e61479cdd5f643`.
- Baseline test blob: `70bfe25e4fb39f3f5198031cfc9e7b9285b49cb4`.
- Read current operating contract, startup/navigation/mission/implementation
  plans, checkpoint, evidence registry, questions, Drive manifest, TGCP research,
  acceptance and direct Graphify dependencies. No assignments or earlier worker
  packets existed at the baseline. The repository's native-review summaries are
  historical evidence claims, not independently revalidated native instructions.
- No local checkout existed. `git status --short --branch` returned exit 128,
  "not a git repository". A connector-fetched local snapshot was materialized;
  all 25 CF2018 source blobs were checked against their Git blob SHA before the
  recorded final test run. No remote clone/gh authentication was assumed.
- Connected Drive search `libapollo` returned no results. A broader `Original`
  search did not establish a target package. The manifest's unpacked-OBB root
  listing returned its `assets` child, not an APK native library. These bounded
  searches are not an exhaustive absence claim. No binary was downloaded,
  fingerprinted or disassembled; complete inventory remains CF18-04's lane.

## Findings with actual scope

| Observation | Evidence and limit |
|---|---|
| Exactly `66 43` passes the model's two-byte predicate | All 65,536 two-byte inputs tested; `43 66` fails. This proves the Python model's configured comparison, not which bytes the actual native receiver expects. |
| Prefix alone passes | A two-byte input contains neither a complete header nor ACK body. `passes=True` therefore cannot mean valid TGCP frame or accepted ACK. |
| Every tested suffix gives the same complete result dictionary | Arbitrary suffix contents and lengths through 4,096 bytes are ignored; appending/removing suffix bytes cannot establish size consistency. No presumed TGCP length-field layout was used. |
| There is no stream reassembly state | Separate one-byte prefix fragments each fail; their concatenation passes. Native receive buffering, wait-versus-reject policy and cursor advancement remain unknown. |
| There is no frame-boundary result | A candidate-prefixed input followed by reversed-prefix synthetic data gives the same result as the first input alone; no consumed length is returned. Native coalescing behavior is untested. |
| Prefix mutation preserves arbitrary suffix data | Minimum accepted input is seven bytes; arbitrary nonframe suffixes pass that threshold. The threshold's native justification is unverified; mutation does not validate header, length, session or key mode. |

The model's module text says "Evidence: native Thumb receiver" and its function
docstring says "known ... native RX compare". With no fingerprinted binary or
reproducible address/branch trace available here, treat that wording as an
unverified historical premise, consistently with TGCP.md and CHECKPOINT.md.

## Native receiver trace still required

No original instruction/address trace is supplied by this packet. Do not fill in
the following from the Python helper or client TX summaries:

1. Exact library/package hash and ISA, symbol-to-address mapping and caller proving
   server-to-client RX use of `tgcpapi_gather_and_split_entire_pkg`.
2. Actual load offset/width, byte swaps and immediate comparison; branch targets
   and error/wait outcomes for both prefix orders.
3. Length-field offset/width/order, what the declared size includes, min/max,
   overflow checks and cursor advancement.
4. Partial-header/body buffering, coalesced-frame consumption and error propagation.
5. Independent `tgcpapi_encrypt_and_send_pkg` TX trace; the historically reported
   client `43 66` prefix cannot establish the opposite RX convention.

Only after those facts are verified should a strict native-aligned parser be
proposed. No parser, server ACK or phone A/B/C execution was added in this audit.

## Reproduction and actual verification

From the snapshot's `cf2018/`, Python stdlib only:

```text
python tools/knowledge.py route 'tgcp ack framing libapollo'
  Routes: [('tgcp', 3), ('sources', 1)]
python tools/knowledge.py doctor
  PASS: required files, links, vault and graph
python -m unittest discover -s tests -v
  Ran 10 tests; OK
python -m unittest discover -s coordination/incoming/CF18-01 -v
  Ran 8 tests; OK
```

Acceptance and negative controls were defined in [ACCEPTANCE.md](ACCEPTANCE.md)
before adding [the audit tests](test_frame_gate_limits.py). They characterize
the Python model only. No live traffic, phone acceptance, original ARM/Thumb
execution, timing measurement, EOF attribution or offline gameplay was tested.

## Integration recipe and next falsifiable action

Only these three lane-owned files are proposed; canonical source, tests, Vault,
Graphify and the root Android app remain unchanged. Coordinator may retain this
packet as a reproducible model-limit audit, run its explicit test command, and
link its limitations into canonical knowledge. If updating canonical wording,
label the native comparison as an unverified historical hypothesis pending
source provenance. Do not promote Q-01, E-09 or G2 based on these tests.

Next falsifiable action: obtain the exact 2018 `libapollo.so` privately via
CF18-04's provenance inventory, establish hash/ISA and RX caller, then trace the
listed validation branches. A clean native trace can confirm or refute the
opposite-prefix hypothesis. Do not substitute the unrelated 9.99 APK. On an
unchanged future activation with no new binary/trace, stop without another audit
or repeated blocker commit.

## Subsequent source-backed packet — 2026-10-30

The user's explicit internet-search instruction enabled recovery of a signed
same-package/version mirror APK. See [native receiver result](NATIVE_RX_RESULT.md)
for actual hashes/signature checks, a bounded GCloud receive/TX trace, native
emulation controls and an original strict parser proposal. It distinguishes a
decoded marker comparison from raw prefix bytes. The earlier model audit above
remains historical; no phone or G2 acceptance is asserted by either packet.
