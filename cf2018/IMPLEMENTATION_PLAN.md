# IMPLEMENTATION PLAN — phase gates

| Gate | Work | Exit evidence |
|---|---|---|
| G0 | Source inventory, permission, APK/XAPK/OBB identity, build controls | hashes, original asset manifest, original-code baseline |
| G1 | Stable no-root local bridge | on-device capture of real client bytes and correct passthrough — **PASS for known TCP targets** |
| G2 | TGCP ACK / auth | authentic client emits a new post-ACK packet, then verified session state — **BLOCKED** |
| G3 | Address discovery | client requests address service and accepts locally issued service address |
| G4 | Update/config/resources | proceeds past Checking for update packages with original assets |
| G5 | Offline identity / lobby | can enter/offline navigate actual game interface without remote dependency |
| G6 | TDM bots | full match, bot AI, damage, scoring, end & replay |
| G7 | Bomb/S&D bots | objectives, bombs, rounds, AI, end & replay |
| G8 | packaging and recovery | repeatable launch, reboot/reinstall controls, no proprietary distribution |

**Immediate high-priority queue:** (1) reconcile native TGCP receive framing `tgcpapi_gather_and_split_entire_pkg` and ACK validation `gcloud_tgcpapi_recv_ack_msg`; (2) audit v0.8 prefix-only test including relay lifecycle; (3) only then authorize one bounded on-device A/B/C; (4) decode next real packet. Do not work on game bot AI while gate G2 is blocked unless a separately evidenced, non-conflicting reverse-engineering research task.

Architecture decisions in [ADR](knowledge-system/vault/decisions/ADR-0001-LOCAL-BRIDGE.md); open questions in [Vault](knowledge-system/vault/OPEN_QUESTIONS.md).
