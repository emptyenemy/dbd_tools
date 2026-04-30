from pathlib import Path

AWS_IP_RANGES_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"

HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
HOSTS_BLOCK_IP = "0.0.0.0"

PING_INTERVAL_SECONDS = 1.0
TCP_PING_TIMEOUT = 2.0
GAME_PORT_MIN = 7777
GAME_PORT_MAX = 7820
SERVER_STALE_SECONDS = 3
NETWORK_CHECK_INTERVAL = 1.0
UI_FPS = 30
INPUT_POLL_SECONDS = 0.015

BANNER_LINES = [
    " ____                 _   ____          ____              _ _       _     _   ",
    "|  _ \\  ___  __ _  __| | | __ ) _   _  |  _ \\  __ _ _   _| (_) __ _| |__ | |_ ",
    "| | | |/ _ \\/ _` |/ _` | |  _ \\| | | | | | | |/ _` | | | | | |/ _` | '_ \\| __|",
    "| |_| |  __/ (_| | (_| | | |_) | |_| | | |_| | (_| | |_| | | | (_| | | | | |_ ",
    "|____/ \\___|\\__,_|\\__,_| |____/ \\__, | |____/ \\__,_|\\__, |_|_|\\__, |_| |_|\\__|",
    "                                |___/               |___/     |___/",
    " _____           _     ",
    "|_   _|__   ___ | |___ ",
    "  | |/ _ \\ / _ \\| / __|",
    "  | | (_) | (_) | \\__ \\",
    "  |_|\\___/ \\___/|_|___/",
]
TAGLINE = "v1.00 by @emptyenemy"
