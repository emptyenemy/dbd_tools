import socket
import time
from concurrent.futures import Executor, as_completed

from . import state
from .config import PING_INTERVAL_SECONDS, TCP_PING_TIMEOUT
from .regions import REGIONS, RegionInfo


def tcp_latency(hostname: str) -> int | None:
    for port in (443, 80):
        start = time.perf_counter()
        try:
            with socket.create_connection((hostname, port), timeout=TCP_PING_TIMEOUT):
                elapsed = int((time.perf_counter() - start) * 1000)
                return max(elapsed, 0)
        except OSError:
            continue
    return None


def ping_all(regions: list[RegionInfo], executor: Executor) -> dict[str, int | None]:
    out: dict[str, int | None] = {}
    futures = {executor.submit(tcp_latency, r.hosts[0]): r.code for r in regions}
    for future in as_completed(futures):
        out[futures[future]] = future.result()
    return out


def ping_loop(executor: Executor) -> None:
    while True:
        new_results = ping_all(REGIONS, executor)
        with state.state_lock:
            state.latest_results.update(new_results)
        time.sleep(PING_INTERVAL_SECONDS)
