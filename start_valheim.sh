#!/bin/bash

export LD_LIBRARY_PATH="./linux64:${LD_LIBRARY_PATH}"
export SteamAppId=892970

SERVER_NAME="Mustachent"
WORLD_NAME="Milfheim"
SERVER_PORT="2456"

exec ./valheim_server.x86_64 \
    -nographics \
    -batchmode \
    -name "$SERVER_NAME" \
    -port "$SERVER_PORT" \
    -world "$WORLD_NAME" \
    -password "$VALHEIM_PASSWORD" \
    -savedir "/srv/valheim/worlds" \
    -saveinterval 1800 \
    -backups 4 \
    -backupshort 7200 \
    -backuplong 43200 \
    -public 1
