import msvcrt
import time

from rich.console import Console
from rich.live import Live

from . import state
from .config import HOSTS_PATH, INPUT_POLL_SECONDS, SERVER_STALE_SECONDS
from .hosts import block_region_hosts, unblock_region_hosts
from .regions import display_order, regions_by_code
from .ui import LiveFrame


def read_key() -> str | None:
    if not msvcrt.kbhit():
        return None
    key = msvcrt.getwch()
    if key == "\x1b":
        return "quit"
    if key in ("\r", "\n"):
        return "block"
    if key in ("\x00", "\xe0"):
        arrow = msvcrt.getwch()
        if arrow == "H":
            return "up"
        if arrow == "P":
            return "down"
        if arrow == "S":
            return "unblock"
    return None


def move_selection(delta: int) -> None:
    with state.state_lock:
        current = state.selected_code
    if current not in display_order:
        state.selected_code = display_order[0]
        return
    idx = display_order.index(current)
    state.selected_code = display_order[(idx + delta) % len(display_order)]


def block_selected() -> None:
    if state.selected_code is None:
        return
    region = regions_by_code.get(state.selected_code)
    if region is not None:
        block_region_hosts(region)


def unblock_selected() -> None:
    if state.selected_code is None:
        return
    region = regions_by_code.get(state.selected_code)
    if region is not None:
        unblock_region_hosts(region)


def render_signature() -> tuple:
    now = time.time()
    with state.state_lock:
        results = tuple(state.latest_results.items())
        selected = state.selected_code
        cs = state.current_server
        stale = cs.last_seen is None or (now - cs.last_seen) > SERVER_STALE_SECONDS
        cur = (cs.ip, cs.port, cs.region_code, cs.error, stale)
    try:
        hosts_mtime = HOSTS_PATH.stat().st_mtime_ns
    except OSError:
        hosts_mtime = 0
    return (results, selected, cur, hosts_mtime)


def main_loop(console: Console) -> None:
    with Live(
        LiveFrame(),
        console=console,
        screen=True,
        auto_refresh=False,
        transient=False,
    ) as live:
        last_sig = None
        while True:
            key = read_key()
            if key == "quit":
                return
            if key == "up":
                move_selection(-1)
            elif key == "down":
                move_selection(1)
            elif key == "unblock":
                unblock_selected()
            elif key == "block":
                block_selected()

            sig = render_signature()
            if sig != last_sig:
                live.refresh()
                last_sig = sig

            time.sleep(INPUT_POLL_SECONDS)
