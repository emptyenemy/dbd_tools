import contextlib
import socket
import struct
import threading
import time

from . import state
from .config import (
    GAME_PORT_MAX,
    GAME_PORT_MIN,
    NETWORK_CHECK_INTERVAL,
    SERVER_STALE_SECONDS,
)


def choose_local_ipv4() -> str:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        try:
            for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
                if not ip.startswith("127."):
                    return ip
        except OSError:
            pass
        return "127.0.0.1"
    finally:
        probe.close()


def parse_udp_game_packet(packet: bytes) -> tuple[str, int] | None:
    if len(packet) < 28:
        return None
    version = packet[0] >> 4
    if version != 4:
        return None
    ip_header_len = (packet[0] & 0x0F) * 4
    if len(packet) < ip_header_len + 8:
        return None
    protocol = packet[9]
    if protocol != 17:
        return None

    src_ip = socket.inet_ntoa(packet[12:16])
    dst_ip = socket.inet_ntoa(packet[16:20])
    src_port, dst_port = struct.unpack("!HH", packet[ip_header_len : ip_header_len + 4])

    src_game = GAME_PORT_MIN <= src_port <= GAME_PORT_MAX
    dst_game = GAME_PORT_MIN <= dst_port <= GAME_PORT_MAX
    if not (src_game or dst_game):
        return None

    if src_game:
        return src_ip, src_port
    return dst_ip, dst_port


class TrafficSniffer:
    def __init__(self, callback) -> None:
        self._callback = callback
        self._socket: socket.socket | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        local_ip = choose_local_ipv4()
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        sock.bind((local_ip, 0))
        sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        self._socket = sock

        with state.state_lock:
            state.current_server.listening_ip = local_ip
            state.current_server.error = None

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        assert self._socket is not None
        while not self._stop.is_set():
            try:
                packet, _ = self._socket.recvfrom(65535)
            except OSError:
                if self._stop.is_set():
                    return
                with state.state_lock:
                    state.current_server.error = "sniffer stopped"
                return
            parsed = parse_udp_game_packet(packet)
            if parsed:
                self._callback(*parsed)

    def stop(self) -> None:
        self._stop.set()
        sock = self._socket
        if sock is not None:
            with contextlib.suppress(Exception):
                sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            with contextlib.suppress(Exception):
                sock.close()
        if self._thread is not None:
            self._thread.join(timeout=0.2)


def on_traffic_detected(ip: str, port: int) -> None:
    with state.state_lock:
        same_ip = state.current_server.ip == ip
        if same_ip and state.current_server.region_name:
            state.current_server.port = port
            state.current_server.last_seen = time.time()
            return

    code = None
    name = None
    try:
        if state.aws_ip_service is not None:
            code, name = state.aws_ip_service.get_region_for_ip(ip)
    except Exception:
        code = None
        name = None

    with state.state_lock:
        state.current_server.ip = ip
        state.current_server.port = port
        state.current_server.region_code = code
        state.current_server.region_name = name
        state.current_server.last_seen = time.time()


def server_watchdog_loop() -> None:
    while True:
        time.sleep(0.5)
        now = time.time()
        with state.state_lock:
            if (
                state.current_server.ip
                and state.current_server.last_seen
                and now - state.current_server.last_seen > SERVER_STALE_SECONDS
            ):
                state.current_server.ip = None
                state.current_server.port = None
                state.current_server.region_code = None
                state.current_server.region_name = None
                state.current_server.last_seen = None


def ensure_sniffer() -> None:
    try:
        desired_ip = choose_local_ipv4()
    except Exception as exc:
        with state.state_lock:
            state.current_server.error = f"network: {exc}"
            state.current_server.listening_ip = None
        return

    with state.sniffer_lock:
        with state.state_lock:
            current_ip = state.current_server.listening_ip

        if state.traffic_sniffer is not None and current_ip == desired_ip:
            return

        if state.traffic_sniffer is not None:
            with contextlib.suppress(Exception):
                state.traffic_sniffer.stop()
            state.traffic_sniffer = None
            with state.state_lock:
                state.current_server.listening_ip = None

        sniffer = TrafficSniffer(on_traffic_detected)
        try:
            sniffer.start()
        except Exception as exc:
            with state.state_lock:
                state.current_server.error = str(exc)
                state.current_server.listening_ip = None
            return

        state.traffic_sniffer = sniffer
        with state.state_lock:
            state.current_server.error = None


def network_watchdog_loop() -> None:
    while True:
        time.sleep(NETWORK_CHECK_INTERVAL)
        ensure_sniffer()
