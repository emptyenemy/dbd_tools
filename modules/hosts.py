import contextlib
import subprocess

from .config import HOSTS_BLOCK_IP, HOSTS_PATH
from .regions import RegionInfo


def normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_hosts_text() -> str:
    try:
        return HOSTS_PATH.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return HOSTS_PATH.read_text(encoding="cp1251", errors="ignore")


def read_hosts_lines() -> list[str]:
    return read_hosts_text().splitlines(keepends=True)


def write_hosts_lines(lines: list[str]) -> None:
    HOSTS_PATH.write_text("".join(lines), encoding="utf-8")


def parse_hosts_line(raw: str) -> tuple[bool, list[str]]:
    stripped = raw.rstrip("\r\n")
    if not stripped.strip():
        return False, []
    code = stripped.strip()
    is_commented = code.startswith("#")
    if is_commented:
        code = code.lstrip("#").strip()
    return is_commented, code.split()


def find_hosts_entries(hostnames: list[str], lines: list[str]) -> list[tuple[int, bool, str]]:
    wanted = {host.lower() for host in hostnames}
    entries: list[tuple[int, bool, str]] = []
    for i, raw in enumerate(lines):
        is_commented, tokens = parse_hosts_line(raw)
        if len(tokens) < 2:
            continue
        ip = tokens[0]
        if any(host.lower() in wanted for host in tokens[1:]):
            entries.append((i, is_commented, ip))
    return entries


def is_region_blocked(region: RegionInfo, lines: list[str]) -> bool:
    return any(
        not is_commented and ip == HOSTS_BLOCK_IP for _, is_commented, ip in find_hosts_entries(region.hosts, lines)
    )


def flush_dns() -> None:
    with contextlib.suppress(Exception):
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=5)


def block_region_hosts(region: RegionInfo) -> None:
    try:
        lines = read_hosts_lines()
    except Exception:
        return

    indices = {idx for idx, _, _ in find_hosts_entries(region.hosts, lines)}
    new_lines = [line for idx, line in enumerate(lines) if idx not in indices]
    if new_lines and not new_lines[-1].endswith(("\n", "\r\n")):
        new_lines[-1] += "\n"
    for host in region.hosts:
        new_lines.append(f"{HOSTS_BLOCK_IP} {host}\n")

    try:
        write_hosts_lines(new_lines)
        flush_dns()
    except Exception:
        return


def unblock_region_hosts(region: RegionInfo) -> None:
    try:
        lines = read_hosts_lines()
    except Exception:
        return

    indices = {idx for idx, _, _ in find_hosts_entries(region.hosts, lines)}
    if not indices:
        return
    new_lines = [line for idx, line in enumerate(lines) if idx not in indices]

    try:
        write_hosts_lines(new_lines)
        flush_dns()
    except Exception:
        return
