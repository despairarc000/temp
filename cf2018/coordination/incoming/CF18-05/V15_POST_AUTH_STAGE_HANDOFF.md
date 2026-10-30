# CF18-05 — v1.5 WAIT/Bingo after confirmed corrected auth

**2026-10-31. Status:** V1.5 BOUNDED TERMUX HARNESS BUILT AND LOCAL TESTED; **NOT PHONE TESTED / NOT AUTHENTICATED**. User's previously paused automations remain unchanged.

## Actual evidence

- The user's real phone v1.4 report [PHONE_V14_RESULT.md](PHONE_V14_RESULT.md) shows corrected 54-byte TGCP `0x2002` response no longer causes immediate local EOF. No third client frame was observed; whether Android processed it as auth is not observed.
- Original native Apollo SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, 5,243,704 bytes, ARM/Thumb inspected with LLVM17, verified hash.
- `TGCPWaitBody::packTLVWithVarint` 0x3b4d16 emits tags `0x10`,`0x20`,`0x30` (position/total/rough-time unsigned varints).
- `TGCPBingoBody::packTLVWithVarint` 0x3b7564 emits `0x15` nested relay, `0x21` compression uint8, `0x30` compression limit varuint32.
- `TGCPRelay::packTLVWithVarint` 0x3b0c38 emits `0x10` position, `0x25` 16-byte identity, `0x30` unsigned 64-bit server ID, `0x40` signed session ID. `TdrWriteBuf::writeVarInt64` at **0x3ac6bc** computes signed ZigZag before varuint64: -1→1 and +1→2.
- `gcloud_tgcpapi_recv_bingo_msg` 0x3ac39e accepts effective `0x3002` or `0x6002`, then parses TGCPBody and takes queue vs relay branch. **Existing native research demonstrates state5 can be reached on mismatched selector/body**, so our strict encoder forbids such mismatch; numeric state5 is NOT proof of legitimate session.

## Original source and tests committed here

- [bingo_wire.py](bingo_wire.py): body-only typed, bounded encoder. All field values explicitly provided by caller. `TGCPBody` wrapper includes its separate `AA + BE uint32(total body length)`. No credential, server identity or valid session generation.
- [bingo_contract.py](bingo_contract.py): deliberately **strict** local structural inspector; not a drop-in native decoder and not proof of game authorization.
- [test_bingo_wire.py](test_bingo_wire.py): 13 offline tests on native-shaped vectors, signed ZigZag edge cases, type correlation, lengths, limits and lack of network dependencies. These were run locally in the conversation (all PASS). They are not original Android tests and require no copyrighted client files.

## User-only v1.5 protocol diagnostic

ChatGPT artifact: `CF2018_TGCP_v1.5_Bingo_Stage_ABC.zip` (20 files, 40,485 bytes, CRC testzip PASS, SHA256 `1a66cede73ecf899dd58651eaef8b1fbebe2021292b48e12e045a8f47ce5fbd3`). Do **not** commit this ZIP to GitHub: it bundles historical authentic SYN hex needed for exact-match target routing.

The six-session opt-in localhost test (two/arm) uses identical 63-byte working AA_DIRECT ACK and exact confirmed v1.4 **54-byte corrected auth packet** in every arm. The following message is delayed 150ms and varies:

| Arm | Additional stage | Meaning |
|---|---|---|
| CORRECTED_ONLY | none | post-auth baseline |
| CORRECTED_WAIT | `0x3002` 60-byte WAIT frame | queue/wait branch experiment |
| CORRECTED_BINGO_SYNTHETIC | `0x6002` 91-byte Bingo frame | fabricated relay/session structural experiment |

Synthetic relay identifier is `CF18LAB-RELAY-01` (16 fake bytes), server_id=1, session_id=1, compression=0. **These are not verified legitimate service/session values** and sending a body does not mean a login occurred. No remote authentication call, APK/OBB edit, background scheduled task, or phone test occurred in the build.

Local verification: **19 PASS**, including typed encoder tests, strict selector/body negative controls, a complete direct listener replay and actual loopback SOCKS5 exchange with synthetic fake client auth request. v1.5 exact stage bytes have NOT been executed through original native Unicorn decoder; ARM source findings are static, so Android runtime is the only live observation if the user opts in.

Opt-in run:
```bash
unzip -o ~/storage/downloads/CF2018_TGCP_v1.5_Bingo_Stage_ABC.zip -d ~
cd ~/CF2018_TGCP_v1.5_Bingo_Stage_ABC
bash START_V15.sh
CF2018_V15_LIVE=YES bash START_V15.sh
```

PCAPdroid SOCKS5 `127.0.0.1:1080`, CrossFire app only, exclude Termux. Report: `Download/CF2018_v15_Bingo_Stage_Result.txt`. It records client frame type/length/SHA256 and proxy reader events only, not tokens or raw auth payloads.

## Interpretation and next gate

If the Bingo arm produces another authentic client frame or changes routing, analyze its structural type/sequence and target while refusing any authentication-success claim. If only WAIT holds open, document wait behavior; if Bingo EOFs quickly, trace first failing native field/relay predicate. If all three behave equally, do not create random identity sweeps; continue native account/session generation and AddressService request predicate research.

Only proof of actual game progression (service request, lobby, functioning gameplay) can advance subsequent gates. Canonical checkpoints and worker queue remain CF18-00-owned; this document is an incoming evidence packet for coordinator review. All automations remain paused.