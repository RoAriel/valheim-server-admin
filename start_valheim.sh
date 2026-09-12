#!/bin/bash
export LD_LIBRARY_PATH="./linux64:${LD_LIBRARY_PATH}"
export SteamAppId=892970

SERVER_NAME="Mustachent"
WORLD_NAME="Milfheim"
SERVER_PORT="2456"

# Cargar modificadores específicos del mundo activo (si existen).
# A diferencia del seed (fijo para siempre desde la generación), estos
# modificadores son reglas de comportamiento en tiempo de ejecución:
# se vuelven a leer en cada arranque, así que cambian con solo reiniciar
# el servidor, sin importar si el mundo ya existía.
MODIFIERS_FILE="/srv/valheim/worlds/modifiers/${WORLD_NAME}.conf"
MODIFIER_ARGS=()
if [[ -f "$MODIFIERS_FILE" ]]; then
    while IFS='=' read -r key value; do
        [[ -z "$key" ]] && continue
        MODIFIER_ARGS+=(-modifier "$key" "$value")
    done < "$MODIFIERS_FILE"
fi

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
    "${MODIFIER_ARGS[@]}" \
    -public 1
