# Configuration DNS/TLS transport control

2026-11-08 UTC. Original CF2018 v1.0.11.11; schedules paused. This is a transport
experiment, not a configuration-success reply or an account/login implementation.

## Question and controls

Can the installed signature-only control A reach a local configuration TLS
endpoint, and does its unchanged trust configuration reject the prepared local
CA? A reached the sign-in UI in the owner's second startup run. No repeat
Google/Facebook sign-in is required. A rejection is expected from the inspected
defaults, but the phone result remains UNKNOWN. If A accepts, revisit runtime
trust and installed APK identity before attributing anything to candidate B.

Later, the separately prepared scoped-trust B can be compared using the same
certificate, with a wrong-CA negative control. B has not been installed or
runtime-tested. The runner's operator label does not attest APK identity.

Immediate acceptance requires observed routing and a discriminating TLS result;
zero DNS or zero TLS traffic is inconclusive. A completed server handshake is
distinct from a received application byte, configuration parsing, accepted
account session and gameplay. No HTTP response is sent by this control.

## Evidence and implementation

CONFIRMED_REPOSITORY_SOURCE: [core](../../../experiments/config_tls_core.py)
`scope_from_extensions` accepts exactly one existing private certificate SAN
matching a configuration-only original hostname fingerprint. Shared/account
hostnames are excluded. `local_dns_answer` changes only that exact name: A maps
to synthetic 198.18.0.18 with TTL0; AAAA returns an empty answer. Unrelated DNS
queries are forwarded unchanged to an IPv4 resolver (default 1.1.1.1).

`patch_redirector` requires SHA256
5952e71ae61d868028f688769eee00e4d10676e9ab66de85dad81e251f617e2a
and adds a private exact-host/synthetic-IP port443 branch to loopback8443.
Existing game8080/8085 and other passthrough paths remain. This does not map all
HTTPS connections. The only proposed PCAPdroid port mappings are DNS UDP/TCP53
to loopback5353, with CrossFire selected and Termux excluded.

CONFIRMED_UPSTREAM_SOURCE, not installed-version proof: PCAPdroid
`DnsSettings.java` validates literal IP DNS values; `PortMapping` matches original
port/protocol rather than hostname. `capture_vpn.c:558–571` applies the mapping
before DNS rewriting/proxy handling. The owner confirms the option is present;
actual phone delivery through it is untested. Earlier proposal context is in
[the current state](../CHECKPOINT.md) and
[trust evidence](ACCOUNT_HTTPS_TRUST_AND_SCOPED_CONTROL.md).

The standalone [runner](../../../tools/run_config_tls_control.py) embeds the
reviewed core, copies an existing version-reply startup privately, and uses the
existing certificate/key folder. It starts no Android application and performs
no installation. Explicit live flags are required. `--check` checks files and
temporarily binds/closes port probes; it starts no listeners or child process.

Limits: 30–180 seconds; 64 DNS queries; 8 selected-name overrides; 4 TLS
connections; 16 concurrent handlers per listener; bounded socket timeouts. Startup
retains its existing 12 sessions, four version lookups/ACKs and per-operation
reply limits. The parent stops when the startup child exits, its time/budget is
exhausted, or Ctrl+C. Only the newly spawned child process group is stopped;
bounded handlers are joined before the unique report is written.

TLS requires matching SNI and TLS1.2 or later. Counters distinguish matched SNI,
handshake completion, client certificate alert, other SSL/transport errors,
post-handshake I/O failure and an application byte. At most one decrypted byte
is read without logging its value. No HTTP/config/account response or account
request body is generated or recorded. Reports contain fixed counts/labels,
`apk_identity_verified=false`, `http_reply_sent=false` and
`login_acceptance=NOT_ESTABLISHED`. Private startup copies/keys stay on device.

## Verification actually performed

SYNTHETIC_ONLY: [15 test methods](../../../tests/test_config_tls_core.py) PASS
with explicit pinned startup, existing private certificate fixture and Apollo
path. UDP/TCP loopback DNS, byte-for-byte unrelated forwarding, exact SOCKS
IP/domain routing, original game routing, synthetic correct-CA acceptance,
wrong-CA and wrong-SNI rejection, post-handshake timeout classification,
process-group cleanup, no-spawn preflight and mocked orchestration/report cleanup
are covered. All SOCKS test outbound connections are guarded to loopback. No
real game endpoint, DNS upstream or Android process was contacted.

Command from repository root (private paths are local prerequisites):

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cf2018/private/analysis_deps \
CF18_PINNED_STARTUP=/workspace/cf2018/private/version_profiles_20261103T051000Z_2e10796b \
CF18_TLS_FIXTURE=/workspace/cf2018/private/config_tls_preflight_check \
CF18_APOLLO_LIBRARY=/workspace/cf2018/coordination/incoming/CF18-04/private/armeabi-v7a-libapollo.so \
python -m unittest discover -s cf2018/tests -p test_config_tls_core.py -q
```

Default suite: 15 run, 12 PASS/3 SKIP for explicitly gated private integration
fixtures. Direct `--check` also passed against local private fixtures. These
checks do not establish Samsung/PCAPdroid/Android TLS acceptance. Knowledge
doctors retain the same 66/114 historical snapshot-omission lines; no new errors.

## Manual phone procedure: installed control A first

1. Keep the currently installed signature-only A. Stop older Termux probes,
   force-stop CrossFire, and stop PCAPdroid capture.
2. Keep CrossFire-only capture, Termux excluded and SOCKS5 127.0.0.1:1080.
   Add/enable two temporary port mappings: UDP original53 to 127.0.0.1:5353;
   TCP original53 to 127.0.0.1:5353. Do not add a port443 rule.
3. Run the command below. At LOCAL CONFIG TLS CONTROL READY, start PCAPdroid
   capture, then open CrossFire. Do not tap Google or Facebook. The script starts
   the existing startup server itself; do not run a second copy.

```bash
(
set -e
D="$HOME/storage/downloads"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/prepare_version_reply.py \
  -o "$D/prepare_version_reply.py"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/run_config_tls_control.py \
  -o "$D/run_config_tls_control.py"
export CF18_APOLLO_LIBRARY="$(python3 "$D/prepare_version_reply.py" --print-library)"
W="$HOME/cf2018_config_tls_startup_$(date +%Y%m%d_%H%M%S)_$$"
P="$HOME/cf2018_private_apk_controls/20261103T113513_850948Z_d9e0adc3"
python3 "$D/prepare_version_reply.py" \
  --source "$HOME/cf2018_directory_identify" --output "$W"
python3 "$D/run_config_tls_control.py" \
  --startup "$W" --prepared-run "$P" --check
CF2018_R037_LIVE_REPLY=YES \
CF2018_VERSION_REPLY=YES \
CF2018_CONFIG_TLS_TEST=YES \
python3 "$D/run_config_tls_control.py" \
  --startup "$W" --prepared-run "$P" --label signature-control --live-opt-in
)
```

After the report is printed, force-stop CrossFire, stop capture and disable or
remove only those two added DNS mappings. Otherwise DNS would point to a stopped
listener. Share only the unique `CF2018_CONFIG_TLS_...txt` in Downloads. No new
ADB pairing, XAPK download or APK installation is needed for this test.

Interpret matched-SNI + explicit certificate alert + no completed handshake as
evidence of rejection on the reached path. Zero traffic, generic SSL errors or
expired startup budgets require routing/context investigation. Successful
handshake/application-byte evidence still does not establish HTTP acceptance,
account login, offline completion or playable bots. Diary remains near its cap;
no append or archival authorized/performed.
