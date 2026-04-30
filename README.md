# Dead by Daylight Tools

TUI utility for Dead by Daylight on Windows: real-time AWS GameLift region ping, region block/unblock via the `hosts` file, and live match server detection through UDP traffic sniffing.

## Features

- **Region ping** — TCP latency to all 15 AWS GameLift regions, refreshed every second.
- **Region blocking** — toggle a region on/off via the Windows `hosts` file. Blocking adds `0.0.0.0` entries for the region's GameLift hosts and flushes the DNS cache.
- **Current server detection** — a raw-socket sniffer captures UDP traffic on the DBD game port range (7777–7820), resolves the remote IP against the live AWS IP ranges feed, and shows which region you are matched into in real time.
- **Network resilience** — the sniffer rebinds automatically when your local IP changes (e.g. switching Wi-Fi/VPN).

## Requirements

- Windows 10/11
- Administrator privileges (needed for raw sockets and to edit `hosts`)
- Python 3.13+ (only if running from source)

## Run

### Prebuilt binary

Download `Dead by Daylight Tools.exe` from [Releases](../../releases) and run it. Windows will prompt for elevation; the binary ships with a UAC manifest.

### From source

```bat
pip install -r requirements.txt
python main.py
```

## Build

Requires [Nuitka](https://nuitka.net/) and a working C compiler (MSVC or MinGW64 — Nuitka can install MinGW64 on first run).

```bat
pip install nuitka
build.bat
```

The output appears in `build/Dead by Daylight Tools.exe`.

## Controls

| Key       | Action                  |
|-----------|-------------------------|
| `↑` / `↓` | Move selection          |
| `Enter`   | Block selected region   |
| `Del`     | Unblock selected region |
| `Esc`     | Exit                    |

## How it works

- **Ping** — opens a short TCP connection to the region's GameLift endpoint on port 443 (falling back to 80) and measures the handshake time. No ICMP, no admin needed for this part alone.
- **Blocking** — appends `0.0.0.0 <gamelift-host>` lines to `C:\Windows\System32\drivers\etc\hosts` for the region's hosts, then runs `ipconfig /flushdns`. Unblock removes those lines.
- **Server detection** — opens a raw `AF_INET` socket with `SIO_RCVALL` on the active LAN interface, parses outbound/inbound UDP packets on ports 7777–7820, and matches the peer IP against AWS's published IP ranges (`https://ip-ranges.amazonaws.com/ip-ranges.json`).

## Notes

- Some antivirus or VPN software interferes with `SIO_RCVALL`. If the sniffer fails to start, the "current server" line will show an error.
- The `hosts` file is edited in place without a backup. Re-run "unblock" or remove the `0.0.0.0` lines manually to revert.

## Disclaimer

Dead by Daylight is a trademark of Behaviour Interactive Inc. This project is an unofficial fan tool and is not affiliated with, endorsed by, or sponsored by Behaviour Interactive.

## License

MIT

---

by [@emptyenemy](https://github.com/emptyenemy)
