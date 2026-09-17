#!/usr/bin/env python3
import a2s
import json
import os
import sys
from datetime import datetime, timedelta

ADDRESS = ("127.0.0.1", 2457)
STATE_FILE = "/var/lib/valheim/players-lastseen.json"
RECENT_MINUTES = 10  # ventana para considerar a alguien "probablemente conectado"

try:
    info = a2s.info(ADDRESS, timeout=3)
    print(f"Jugadores conectados: {info.player_count}/{info.max_players}")
except Exception as e:
    print(f"No se pudo consultar el servidor: {e}", file=sys.stderr)
    sys.exit(1)

if not os.path.exists(STATE_FILE):
    print("(sin datos de actividad reciente todavía; el tracker corre cada 5 min vía cron)")
    sys.exit(0)

with open(STATE_FILE) as f:
    try:
        state = json.load(f)
    except json.JSONDecodeError:
        state = {}

now = datetime.now()
recent = []
for name, ts in state.items():
    try:
        seen = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        continue
    if now - seen <= timedelta(minutes=RECENT_MINUTES):
        recent.append((name, ts))

if recent:
    print(f"Actividad detectada en los últimos {RECENT_MINUTES} min (por logs, aproximado):")
    for name, ts in sorted(recent, key=lambda x: x[1], reverse=True):
        print(f"  - {name}  (última actividad: {ts})")
else:
    print(f"Sin actividad de nombres detectada en los últimos {RECENT_MINUTES} min.")
