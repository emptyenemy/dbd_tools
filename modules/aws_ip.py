import ipaddress
import json
import threading
import urllib.request

from .config import AWS_IP_RANGES_URL
from .regions import regions_by_code


class AwsIpService:
    def __init__(self) -> None:
        self._ranges: list[tuple[ipaddress.IPv4Network, str, str]] = []
        self._lock = threading.Lock()

    def _refresh_locked(self) -> None:
        if self._ranges:
            return
        req = urllib.request.Request(AWS_IP_RANGES_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="ignore"))

        ranges: list[tuple[ipaddress.IPv4Network, str, str]] = []
        for item in payload.get("prefixes", []):
            cidr = item.get("ip_prefix")
            region = item.get("region") or ""
            border_group = item.get("network_border_group") or region
            if not cidr or not region:
                continue
            try:
                network = ipaddress.ip_network(cidr, strict=False)
            except ValueError:
                continue
            if network.version != 4:
                continue
            ranges.append((network, border_group, region))

        ranges.sort(key=lambda row: row[0].prefixlen, reverse=True)
        self._ranges = ranges

    def get_region_for_ip(self, ip: str) -> tuple[str | None, str | None]:
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            return None, None
        if ip_obj.version != 4:
            return None, None

        with self._lock:
            self._refresh_locked()
            ranges = list(self._ranges)

        for network, border_group, region in ranges:
            if ip_obj not in network:
                continue
            code = border_group if border_group in regions_by_code else region
            if code in regions_by_code:
                return code, regions_by_code[code].name
            return code, code

        return None, None
