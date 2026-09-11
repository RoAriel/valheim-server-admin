#!/bin/bash
LOG_FILE="/var/log/valheim-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if systemctl is-active --quiet valheim; then
    STATUS="UP"
else
    STATUS="DOWN"
fi

LAST_STATUS=$(tail -n 1 "$LOG_FILE" 2>/dev/null | grep -oE '(UP|DOWN)$')

if [[ "$STATUS" != "$LAST_STATUS" ]]; then
    echo "${TIMESTAMP} - Estado del servidor: ${STATUS}" >> "$LOG_FILE"
fi
