"""Private-source integration subprocess. All sockets are local synthetic peers."""
import asyncio
from pathlib import Path
import socket
import tempfile
import threading
import json

from cf2018_redirector import Redirector, parser, is_game_target
from routed_probe_v38 import Run, Server, report
from tests.test_v38 import frame
from tests.test_v17 import make_client_frame
from tests_helper_v18 import recv_exact
from tgcp_body_repair_v14 import candidate
from stage_frame_v15 import candidate_stage
from preflight_v09 import strict_header_candidate
from ack_wire import make_candidate_ack
from apollo_wire import request_query_addr


async def control():
    assert is_game_target('45.113.69.32', 8080)
    assert is_game_target('211.159.211.105', 8085)
    for host, port in [('45.113.69.32', 443), ('127.0.0.1', 8080),
                       ('dir.3.1562854559.agcloudcs.com', 8080), ('example.invalid', 8085)]:
        assert not is_game_target(host, port)
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        run = Run(temp / 'run', max_sessions=4)
        server = Server(('127.0.0.1', 0), run)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        args = parser().parse_args(['--mode', 'forward', '--log-dir', str(run.base / 'relay'),
                                  '--emulator-port-8080', str(server.server_address[1])])
        relay = Redirector(args)
        proxy = await asyncio.start_server(relay.handle, '127.0.0.1', 0)
        address = proxy.sockets[0].getsockname()
        syn = bytes.fromhex(Path('golden_request.hex').read_text().strip())

        async def echo(reader, writer):
            writer.write(await reader.read(100))
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        unrelated = await asyncio.start_server(echo, '127.0.0.1', 0)
        unrelated_port = unrelated.sockets[0].getsockname()[1]

        def trials():
            # Non-game IP+port keeps ordinary binary-safe passthrough.
            with socket.create_connection(address, timeout=4) as other:
                other.settimeout(4)
                connect = b'\x05\x01\x00\x01' + socket.inet_aton('127.0.0.1') + unrelated_port.to_bytes(2, 'big')
                other.sendall(b'\x05\x01\x00' + connect + b'\x00\xffPASSTHROUGH')
                assert recv_exact(other, 2) == b'\x05\x00'
                assert recv_exact(other, 10) == b'\x05\x00\x00\x01' + bytes(6)
                assert recv_exact(other, 13) == b'\x00\xffPASSTHROUGH'
            for _ in range(4):
                with socket.create_connection(address, timeout=4) as client:
                    client.settimeout(4)
                    # Pipeline greeting, CONNECT and TGCP input: buffered bytes must survive.
                    connect = b'\x05\x01\x00\x01' + socket.inet_aton('45.113.69.32') + (8080).to_bytes(2, 'big')
                    client.sendall(b'\x05\x01\x00' + connect + syn)
                    assert recv_exact(client, 2) == b'\x05\x00'
                    assert recv_exact(client, 10) == b'\x05\x00\x00\x01' + bytes(6)
                    assert recv_exact(client, 63) == strict_header_candidate(make_candidate_ack(syn))
                    client.sendall(make_client_frame(0x2001, b'X' * 73))
                    assert recv_exact(client, 54) == candidate('V14_BODY_ENVELOPED')
                    assert recv_exact(client, 91) == candidate_stage('CORRECTED_BINGO_SYNTHETIC')
                    body = (1).to_bytes(4, 'big') + request_query_addr(1, 1, 'PRIVATE_CANARY', 1)
                    client.sendall(frame(0, body, b'QueryAddrSvr'))
                    assert client.recv(1) == b''
            assert run.done.wait(3)

        try:
            await asyncio.wait_for(asyncio.to_thread(trials), timeout=20)
            await asyncio.sleep(0.1)
            text = report(run, temp / 'result.txt').read_text()
            events = [json.loads(x) for x in run.log.read_text().splitlines()]
            accepted = [e for e in events if e['action'] == 'accepted']
            later = [e for e in events if e['action'] == 'later_client_frame']
            assert len(accepted) == len(later) == 4
            assert len({e['cid'] for e in accepted}) == 4
            assert len({e['run_id'] for e in accepted}) == 1
            assert 'RUN_ID=' in text and 'cid=' in text
            assert text.count('sequence_prefix=MATCH') == 4
            assert text.count('legacy_after_sequence=LEGACY_HEADER_PLAUSIBLE') == 4
            assert text.count('known_address_route=MATCH') == 4
            assert all(token not in text + run.log.read_text() for token in ('PRIVATE_CANARY', 'QueryAddrSvr'))
            assert not list(run.base.rglob('capture_*.bin'))
            relay_events = [json.loads(x) for x in relay.log_path.read_text().splitlines()]
            assert sum(e['event'] == 'CONNECTED' and e['status'] == 'EMULATOR' for e in relay_events) == 4
            assert sum(e['event'] == 'CONNECTED' and e['status'] == 'PASSTHROUGH' for e in relay_events) == 1
            assert any(e['event'] == 'RELAY_READ_EOF' for e in relay_events)
            print(json.dumps({'sessions': 4, 'privacy_pass': True, 'stage_bytes_unchanged': True,
                              'scope': 'LINUX_LOCAL_SOCKS5_NOT_ANDROID_PHONE'}))
        finally:
            proxy.close()
            await proxy.wait_closed()
            unrelated.close()
            await unrelated.wait_closed()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


asyncio.run(control())
