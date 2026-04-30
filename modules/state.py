import threading
from dataclasses import dataclass

from .regions import REGIONS


@dataclass
class CurrentServer:
    ip: str | None = None
    port: int | None = None
    region_code: str | None = None
    region_name: str | None = None
    last_seen: float | None = None
    listening_ip: str | None = None
    error: str | None = None


state_lock = threading.Lock()
sniffer_lock = threading.Lock()
latest_results: dict[str, int | None] = {r.code: None for r in REGIONS}
selected_code: str | None = REGIONS[0].code
current_server = CurrentServer()
aws_ip_service = None
traffic_sniffer = None
