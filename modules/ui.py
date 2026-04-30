import time

from rich.console import Group
from rich.table import Table
from rich.text import Text

from . import state
from .config import BANNER_LINES, SERVER_STALE_SECONDS, TAGLINE
from .hosts import is_region_blocked, read_hosts_lines
from .regions import REGIONS
from .state import CurrentServer


def banner_renderable() -> Group:
    items = [Text(line, style="bold blue") for line in BANNER_LINES]
    items.append(Text(""))
    items.append(Text(TAGLINE, style="dim"))
    return Group(*items)


def ping_style(ping: int | None) -> str:
    if ping is None:
        return "bold red"
    if ping < 50:
        return "bold green"
    if ping < 100:
        return "bold yellow"
    return "bold red"


def current_server_text() -> Text:
    with state.state_lock:
        cur = CurrentServer(
            ip=state.current_server.ip,
            port=state.current_server.port,
            region_code=state.current_server.region_code,
            region_name=state.current_server.region_name,
            last_seen=state.current_server.last_seen,
            listening_ip=state.current_server.listening_ip,
            error=state.current_server.error,
        )

    label = ("Текущий сервер: ", "bold blue")

    if cur.error or not cur.ip:
        return Text.assemble(label, ("ожидается...", "white"))

    age = int(time.time() - cur.last_seen) if cur.last_seen else 0
    if age > SERVER_STALE_SECONDS:
        return Text.assemble(label, ("ожидается...", "white"))

    endpoint = f"{cur.ip}:{cur.port}" if cur.port else cur.ip
    region = cur.region_name or "Unknown"
    return Text.assemble(
        label,
        (f"{region} ", "white"),
        (f"[{endpoint}]", "bold blue"),
    )


def build_frame() -> Group:
    with state.state_lock:
        results = dict(state.latest_results)
        selected = state.selected_code

    try:
        hosts_lines = read_hosts_lines()
    except Exception:
        hosts_lines = []

    table = Table.grid(padding=(0, 2))
    table.add_column(no_wrap=True)
    table.add_column(no_wrap=True)
    table.add_column(no_wrap=True, justify="right", min_width=6)
    table.add_column(no_wrap=True)

    for region in REGIONS:
        is_selected = region.code == selected
        ping = results.get(region.code)
        blocked = is_region_blocked(region, hosts_lines)

        marker = Text(">", style="bold blue") if is_selected else Text(" ")
        name_style = "bold blue" if is_selected else ""
        name = Text(region.name, style=name_style)
        ping_text = Text("💀", style="bold red") if ping is None else Text(f"{ping}ms", style=ping_style(ping))
        tag = Text("[заблокирован]", style="bold red") if blocked else Text("[не заблокирован]", style="bold green")
        table.add_row(marker, name, ping_text, tag)

    footer = Text(
        "↑/↓ — перемещение, ENTER — заблокировать, DEL — разблокировать, ESC — выход",
        style="dim",
    )

    return Group(
        banner_renderable(),
        Text(""),
        current_server_text(),
        Text(""),
        Text("Список серверов:", style="bold blue"),
        table,
        Text(""),
        footer,
    )


class LiveFrame:
    def __rich__(self):
        return build_frame()
