#!/usr/bin/env python3
import a2s
import sys

ADDRESS = ("127.0.0.1", 2457)

try:
    players = a2s.players(ADDRESS, timeout=3)
except Exception as e:
    print(f"No se pudo consultar el servidor: {e}", file=sys.stderr)
    sys.exit(1)

players = [p for p in players if p.name]

if not players:
    print("0 jugadores conectados ahora mismo.")
else:
    print(f"{len(players)} jugador(es) conectado(s) ahora mismo:")
    for p in players:
        mins = int(p.duration // 60)
        secs = int(p.duration % 60)
        print(f"  - {p.name}  (conectado hace {mins}m {secs}s)")
