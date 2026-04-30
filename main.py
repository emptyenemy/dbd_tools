import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from rich.console import Console

from modules import state
from modules.admin import is_admin, relaunch_as_admin
from modules.aws_ip import AwsIpService
from modules.controls import main_loop
from modules.ping import ping_all, ping_loop
from modules.regions import REGIONS
from modules.sniffer import ensure_sniffer, network_watchdog_loop, server_watchdog_loop


def main() -> None:
    console = Console()

    if os.name != "nt":
        console.print("[red]Этот скрипт работает только на Windows.[/]")
        sys.exit(1)

    if not is_admin():
        rc = relaunch_as_admin()
        sys.exit(0 if rc > 32 else 1)

    state.aws_ip_service = AwsIpService()
    ensure_sniffer()

    ping_executor = ThreadPoolExecutor(max_workers=16, thread_name_prefix="ping")

    initial = ping_all(REGIONS, ping_executor)
    with state.state_lock:
        state.latest_results.update(initial)

    threading.Thread(target=ping_loop, args=(ping_executor,), daemon=True).start()
    threading.Thread(target=server_watchdog_loop, daemon=True).start()
    threading.Thread(target=network_watchdog_loop, daemon=True).start()

    try:
        main_loop(console)
    except KeyboardInterrupt:
        pass
    finally:
        if state.traffic_sniffer is not None:
            state.traffic_sniffer.stop()
        ping_executor.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    main()
