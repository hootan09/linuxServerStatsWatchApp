#!/usr/bin/env python3
import json
import time
import pathlib
import subprocess
from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Linux-Watch Stats")

# allow the local HTML file (or any) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# tiny helpers
# ------------------------------------------------------------------
def sh(cmd: str) -> str:
    """Run shell command and return stdout stripped."""
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def uptime_seconds() -> float:
    with open("/proc/uptime") as f:
        return float(f.read().split()[0])

def human_time(sec: float) -> str:
    d = int(sec // 86400)
    h = int((sec % 86400) // 3600)
    m = int((sec % 3600) // 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    parts.append(f"{m}m")
    return " ".join(parts)

def bytes_to_MB(rx: int, tx: int) -> tuple[float, float]:
    # convert bytes → MiB
    return round(rx / 1024 / 1024, 1), round(tx / 1024 / 1024, 1)

# ------------------------------------------------------------------
# main collector
# ------------------------------------------------------------------
def get_stats() -> Dict:
    # ---- time -----------------------------------------------------
    now = datetime.now().strftime("%H:%M:%S")

    # ---- battery (if laptop) --------------------------------------
    bat_path = pathlib.Path("/sys/class/power_supply/BAT0/capacity")
    bat = int(bat_path.read_text().strip()) if bat_path.exists() else 0

    # ---- CPU (rough 1-second average) -----------------------------
    def cpu_usage():
        with open("/proc/stat") as f:
            line = f.readline()
        vals = list(map(int, line.split()[1:]))
        idle1, total1 = vals[3], sum(vals)
        time.sleep(0.5)
        with open("/proc/stat") as f:
            line = f.readline()
        vals = list(map(int, line.split()[1:]))
        idle2, total2 = vals[3], sum(vals)
        return round(100 * (1 - (idle2 - idle1) / (total2 - total1)), 1)

    cpu = cpu_usage()

    # ---- memory ---------------------------------------------------
    meminfo = {}
    for ln in pathlib.Path("/proc/meminfo").read_text().splitlines():
        if ln:
            k, v = ln.split(":")[:2]
            meminfo[k] = int(v.split()[0])  # kB
    mem_total = meminfo["MemTotal"] // 1024  # → MB
    mem_avail = meminfo["MemAvailable"] // 1024
    mem_used = mem_total - mem_avail

    # ---- disk -----------------------------------------------------
    # df -h output:  Filesystem  Size  Used  Avail  Use%  Mount
    root_line = sh("df -h / | tail -1").split()
    home_line = sh("df -h $HOME | tail -1").split()
    disk_total, disk_used, disk_avail = root_line[1], root_line[2], root_line[3]
    home_free = home_line[3]

    # ---- uptime / load -------------------------------------------
    up_sec = uptime_seconds()
    uptime_str = human_time(up_sec)
    load_1, load_5, load_15 = sh("cut -d' ' -f1-3 /proc/loadavg").split()

    # ---- network --------------------------------------------------
    # pick first non-loopback interface
    net_data = pathlib.Path("/proc/net/dev").read_text()
    iface = ""
    rx_bytes = tx_bytes = 0
    for ln in net_data.splitlines():
        if "lo:" in ln:
            continue
        if ":" in ln:
            parts = ln.split()
            iface = parts[0].rstrip(":")
            rx_bytes, tx_bytes = int(parts[1]), int(parts[9])
            break
    rx_mb, tx_mb = bytes_to_MB(rx_bytes, tx_bytes)

    # ---- process count -------------------------------------------
    procs = int(sh("ps -e --no-headers | wc -l"))

    # ---- temperature (generic thermal zone0) ----------------------
    try:
        temp = int(open("/sys/class/thermal/thermal_zone0/talc").read()) // 1000
    except Exception:
        temp = 0

    # ---- compose JSON --------------------------------------------
    return {
        "time": now,
        "bat": bat,
        "cpu": cpu,
        "memUsed": mem_used,
        "memTotal": mem_total,
        "diskTotal": disk_total,
        "diskUsed": disk_used,
        "diskAvail": disk_avail,
        "homeFree": home_free,
        "uptime": uptime_str,
        "load": f"{load_1} {load_5} {load_15}",
        "net": {"iface": iface, "rx": rx_mb, "tx": tx_mb},
        "procs": procs,
        "temp": temp,
    }

# ------------------------------------------------------------------
# route
# ------------------------------------------------------------------
@app.get("/stats")
def stats():
    return get_stats()

# ------------------------------------------------------------------
# entry
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)