import msvcrt
import time

from rich.console import Console
from rich.live import Live

from . import state
from .config import INPUT_POLL_SECONDS, UI_FPS
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


def main_loop(console: Console) -> None:
    with Live(
        LiveFrame(),
        console=console,
        screen=True,
        refresh_per_second=UI_FPS,
        transient=False,
    ):
        while True:
            key = read_key()
            if key is None:
                time.sleep(INPUT_POLL_SECONDS)
                continue
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
