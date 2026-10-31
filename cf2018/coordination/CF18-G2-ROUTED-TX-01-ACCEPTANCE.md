# Server priority and routed-TX acceptance

Base5d76e82696984717e394552cc6fb9c076e77e01f,2026-10-31.
Review incoming phone14/15/16 independently of stale canonical checkpoint.
Prefer local-server continuation based on authentic later traffic, not a claim
of halfway completion. Integrity remains parked, schedules paused.
Execute pinned original send-with-route with independent synthetic payload/context,
stop before encryption/send. Verify prefix length/account dataflow and selected
type. Negative controls: state4, initialization, oversize, missing route pointer,
invalid timeout. Never emit a real reply or infer valid account from injected5.
Publish only original controls/metadata; no original payload, private identity,
native dump or binary. Run canonical tests/doctor and record actual counts.
