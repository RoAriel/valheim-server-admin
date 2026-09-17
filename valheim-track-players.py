#!/usr/bin/env python3
import a2s
import json
import os
from datetime import datetime

ADDRESS = ("127.0.0.1", 2457)
STATE_FILE = "/var/lib/valheim/players-lastseen.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    try:
        players = a2s.players(ADDRESS, timeout=3)
    except Exception:
        return  # servidor caído o sin responder: no se actualiza nada, se reintenta en 5 min

    state = load_state()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for p in players:
        if p.name:
            state[p.name] = now
    save_state(state)

if __name__ == "__main__":
    main()
