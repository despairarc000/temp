# CF18-05 — v1.6 routed application fingerprint (independent local handoff)

**2026-10-31.** Two-session **offline-tested / NOT PHONE-TESTED** diagnostic, built from exactly verified v1.5. No original APK/OBB changes, no real auth, no new schedules. All code stays under the CF18-05 incoming lane pending CF18-00 review.

## Verified evidence behind this step

- [v1.5 phone report](PHONE_V15_RESULT.md): six sessions; the **two synthetic Bingo** sessions emitted authentic client type `0x4013` frames (161 and 166 bytes) at 23.46 and 15.39 ms after Bingo; WAIT and corrected-auth-only arms emitted no new client frame. Neither application body nor a real authenticated session was captured.
- In exact hash-pinned original `libapollo.so` SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, 5,243,704 bytes, ARM Thumb: `gcloud_tgcpapi_send_with_route` at `0x3a91ec` checks numeric state 5 at `0x3a9318-0x3a931e`, emits decoded base marker `0x4366` at `0x3a9372-0x3a937c`, extension `0x4013` at `0x3a9390-0x3a9394`, then invokes **tgcpapi_encrypt_and_send_pkg** at `0x3a941c`. Therefore `0x4013` describes routed client traffic; it is not by itself a `QueryAddrInfo` RPC type, authentication token or game login proof.
- Independent static `AddressService::Send_QueryAddrInfo` `0x3998d4` invokes a virtual RPC-protocol write-message begin at `0x399902-0x399904`, writes `QueryAddrSvr_QueryAddrInfo_pargs` at `0x39991c`, then delegates to virtual protocol/message-buffer interfaces. It may produce application payload but no actual relationship to v1.5 body is proven.
- A Thrift-style named method and sequence is a **candidate structural signature** based on the previously recovered native RPC protocols. Actual selected wire protocol, compression, encryption and opaque inner container are unknown.

## Reusable original code committed

- [route_fingerprint_v16.py](route_fingerprint_v16.py): a bounded, **privacy-minimal** observer that runs on a validated `0x4013` frame in memory; inspects body length, envelope hint and up to 96 offsets for **exact allowlisted** service methods with length/type/8-byte-sequence shape. Returns only the known method label (or NOT_IDENTIFIED/AMBIGUOUS), offset and type label. No byte prefixes, raw payload, sequence values, tokens, personal IDs, IPs, free-text strings, decompression or device packet bytes are persisted.
- [install_v16.py](install_v16.py): creates `route_probe_v16.py` + `START_V16.sh` **inside existing user-owned v1.5 folder** from exact SHA256-pinned `stage_probe_v15.py`. It verifies generated source SHA256 `054ded025008667df931c34495f29999b1805d12529250057caf9e91a5e1fbb2` and startup SHA256 `4b00d396ca0d438e1930dfcffd6d9a5351477eadcb4d05d9a2b909756223126d`, without editing v1.5 source.
- [test_v16_route.py](test_v16_route.py): **14 local PASS**, including exact known/unknown allowlist signatures, false-positive controls, bounds, direct loopback and real local SOCKS5 passthrough to the emulated listener. No actual phone run. The tests synthesize the client-side packet structure; no captured authentication payload is published.
- Startup checks are offline by default; live requires `CF2018_V16_LIVE=YES`, with max **two** Bingo-only synthetic-stage sessions. It preserves the verified ACK63, corrected auth54 and synthetic Bingo91 from v1.5; sends **no `0x4013` server reply**.

## Termux installation, no full ZIP

The user already ran v1.5 successfully. From the existing `~/CF2018_TGCP_v1.5_Bingo_Stage_ABC` folder, use the following **three public source-file downloads**. All content is independent original Python code and contains **no historical golden_request.hex**. The installed v1.5 package already has that private file.

```bash
cd "$HOME/CF2018_TGCP_v1.5_Bingo_Stage_ABC" || exit 1
BASE="https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/coordination/incoming/CF18-05"
curl -fLsS "$BASE/route_fingerprint_v16.py" -o route_fingerprint_v16.py
curl -fLsS "$BASE/install_v16.py" -o install_v16.py
mkdir -p tests
curl -fLsS "$BASE/test_v16_route.py" -o tests/test_v16_route.py
python install_v16.py
bash START_V16.sh
```

Then stop earlier listeners on 8080/8085/1080, keep PCAPdroid filtering **only CrossFire**, SOCKS5 `127.0.0.1:1080`, exclude Termux, and explicitly opt in:

```bash
CF2018_V16_LIVE=YES bash START_V16.sh
```

Expected report: `Download/CF2018_v16_Routed_Fingerprint_Result.txt` with two `ROUTED_HINT` lines if two complete `0x4013` frames are observed. The report contains only structural labels and timings. It does **not** reproduce or reveal actual RPC request data.

If `method=QueryAddrInfo`: treat only as an allowlisted **signature hint**, then independently validate surrounding RPC framing and callback/sequence semantics before writing a reply. If `NOT_IDENTIFIED`: **do not infer encryption** or assume it is not AddressService; the message might use another protocol, a different offset, compression or encryption. If no `0x4013`: record the differential outcome; do not retry arbitrary session/account values.

All phone, account, service and gameplay acceptance gates remain unverified. No scheduled work was enabled.
