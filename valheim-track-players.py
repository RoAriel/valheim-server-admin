#!/usr/bin/env python3
import json
import os
import re
import subprocess
from datetime import datetime

STATE_FILE = "/var/lib/valheim/players-lastseen.json"
PATTERN = re.compile(r"Got character ZDOID from (.+?) :")

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
    # Ventana de 6 min para no perder actividad entre corridas del cron (cada 5 min)
    try:
        result = subprocess.run(
            ["journalctl", "-u", "valheim", "--since", "6 min ago", "--no-pager", "-o", "cat"],
            capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return

    names = set(PATTERN.findall(result.stdout))
    if not names:
        return

    state = load_state()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for name in names:
        state[name] = now
    save_state(state)

if __name__ == "__main__":
    main()
