![valheim-banner.png](https://i.postimg.cc/ht4S1m96/valheim-banner.png)

# Guía técnica — Servidor dedicado de Valheim

Guía paso a paso para levantar, asegurar y administrar un servidor dedicado de Valheim en una VPS Ubuntu, incluyendo la herramienta de administración `vhctl` construida a lo largo del proceso.

> 🗓️ **Última revisión**: incluye la corrección del bug de `-crossplay`, soporte de modificadores de mundo (con la corrección de que sí aplican a mundos existentes con un reinicio), versionado con git local, y monitorización básica. El script `vhctl` completo vive en [`vhctl.sh`](./vhctl.sh) — esta guía referencia ese archivo en vez de repetirlo entero en cada paso.

## 📑 Índice

**Parte 1 — Preparación del sistema**
- [[#1. Conectarse por SSH al servidor]]
- [[#2. Crear el usuario del servidor]]
- [[#3. Instalar paquetes básicos del sistema]]
- [[#4. Configurar el firewall (UFW)]]
- [[#5. Instalar SteamCMD]]
- [[#6. Crear los directorios del servidor]]

**Parte 2 — Instalación y arranque de Valheim**
- [[#7. Instalar Valheim Dedicated Server]]
- [[#8. Crear el script de arranque]]
- [[#9. Configurar el archivo de variables de entorno]]
- [[#10. Crear el servicio systemd]]
- [[#11. Habilitar e iniciar el servicio]]
- [[#12. Verificar que arrancó correctamente]]
- [[#13. Probar el ciclo de reinicio]]

**Parte 3 — Backups, resiliencia y conectividad**
- [[#14. Configurar backups nativos de Valheim]]
- [[#15. Reiniciar y comprobar backups]]
- [[#16. Resolver el bug de conexión de `-crossplay`|16. Resolver el bug de conexión de -crossplay]]
- [[#17. Verificar los backups generados]]
- [[#18. Configurar backup externo manual con FileZilla]]
- [[#19. Probar la restauración de un backup]]

**Parte 4 — Administración avanzada con `vhctl`**
- [[#20. Construir la herramienta de gestión `vhctl`|20. Construir la herramienta de gestión vhctl]]
- [[#21. Habilitar sudo sin contraseña para `vhctl`|21. Habilitar sudo sin contraseña para vhctl]]
- [[#22. Versionar la configuración con git]]
- [[#23. Configurar monitorización básica]]
- [[#24. Configurar modificadores de mundo]]
- [[#25. Configurar la zona horaria del servidor]]
- [[#26. Ver jugadores conectados y su último acceso]]

## 0. Datos del servidor/proyecto

| Dato | Valor |
|---|---|
| Hostname | `mustachent.baires.host` |
| IP principal | `23.175.40.29` |
| Contraseña root | `PASSWORD_SERVER` |

> ⚠️ **Nota**: reemplazá `PASSWORD_SERVER`, `PASSWORD_USER_VALHEIM`, `NOMBRE_SERVER`, `NOMBRE_MUNDO` y `PASSWORD_MUNDO` por tus valores reales antes de usar esta guía, y no la compartas ya completada con las contraseñas reales. Un placeholder sin reemplazar en `start_valheim.sh` no rompe el script, pero hace que Valheim genere un mundo nuevo vacío con ese nombre literal en vez de cargar el tuyo — pasó una vez en este proyecto (ver Changelog).

---

# Parte 1 — Preparación del sistema

## 1. Conectarse por SSH al servidor

```bash
ssh root@23.175.40.29
```

## 2. Crear el usuario del servidor

**Crear el usuario:**
```bash
adduser valheim
# Contraseña: PASSWORD_USER_VALHEIM
```

**Agregar el usuario al grupo de administradores:**
```bash
usermod -aG sudo valheim
```

## 3. Instalar paquetes básicos del sistema

```bash
apt install -y curl wget unzip tar ca-certificates software-properties-common htop nano
```

## 4. Configurar el firewall (UFW)

Antes de instalar y arrancar Valheim, dejamos el firewall configurado aplicando mínimo privilegio: por Internet solo quedan expuestos los servicios que realmente necesitamos.

### Instalar UFW
```bash
apt install -y ufw
```

### Permitir SSH antes de activar el firewall
(para no perder el acceso remoto)
```bash
ufw allow OpenSSH
```

### Permitir los puertos de Valheim
```bash
ufw allow 2456:2457/udp
```

### Activar las reglas
```bash
ufw enable
```

### Comprobar las reglas
```bash
ufw status verbose
```

## 5. Instalar SteamCMD

```bash
add-apt-repository multiverse
dpkg --add-architecture i386
apt update
apt install -y steamcmd
command -v steamcmd
steamcmd +quit
```

## 6. Crear los directorios del servidor

```bash
mkdir -p /opt/valheim-server
mkdir -p /srv/valheim/worlds

chown -R valheim:valheim /opt/valheim-server
chown -R valheim:valheim /srv/valheim

chmod 755 /opt/valheim-server
chmod 755 /srv/valheim
chmod 750 /srv/valheim/worlds
```

> ⚠️ **Actualización respecto a la guía original**: acá también se creaba `/srv/valheim/backups`, pensada como destino de los backups. En la práctica no se usa: Valheim guarda sus backups nativos en una subcarpeta que crea automáticamente dentro de `/srv/valheim/worlds` (ver paso 15), y los backups de `vhctl` se guardan en otra subcarpeta al mismo nivel (ver paso 20). Por eso se quitó la creación de `/srv/valheim/backups` de este paso — si ya la creaste en un servidor existente y no la estás usando, se puede borrar sin problema (`rmdir /srv/valheim/backups`, si está vacía).

---

# Parte 2 — Instalación y arranque de Valheim

## 7. Instalar Valheim Dedicated Server

**Cambiar al usuario `valheim`:**
```bash
su - valheim
```

**Instalar el servidor vía SteamCMD:**
```bash
steamcmd +force_install_dir /opt/valheim-server +login anonymous +app_update 896660 validate +quit
```

## 8. Crear el script de arranque

**Crear el archivo:**
```bash
nano /opt/valheim-server/start_valheim.sh
```

Contenido:

```bash
#!/bin/bash
export LD_LIBRARY_PATH="./linux64:${LD_LIBRARY_PATH}"
export SteamAppId=892970

SERVER_NAME="NOMBRE_SERVER"
WORLD_NAME="NOMBRE_MUNDO"
SERVER_PORT="2456"

exec ./valheim_server.x86_64 \
    -nographics \
    -batchmode \
    -name "$SERVER_NAME" \
    -port "$SERVER_PORT" \
    -world "$WORLD_NAME" \
    -password "$VALHEIM_PASSWORD" \
    -crossplay \
    -savedir "/srv/valheim/worlds" \
    -public 1
```

**Dar permisos de ejecución:**
```bash
chmod 750 /opt/valheim-server/start_valheim.sh
```

## 9. Configurar el archivo de variables de entorno

Salir del usuario `valheim` y volver a `root` para generar el `.env` con la contraseña del mundo.

**Crear el archivo (como `root`):**
```bash
nano /etc/valheim-server.env
```

Contenido:

```
VALHEIM_PASSWORD="PASSWORD_MUNDO"
```

**Ajustar permisos:**
```bash
chown root:valheim /etc/valheim-server.env
chmod 640 /etc/valheim-server.env
```

## 10. Crear el servicio systemd

**Crear la unidad:**
```bash
nano /etc/systemd/system/valheim.service
```

Contenido:

```ini
[Unit]
Description=Valheim Dedicated Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=valheim
Group=valheim
WorkingDirectory=/opt/valheim-server
EnvironmentFile=/etc/valheim-server.env
ExecStart=/opt/valheim-server/start_valheim.sh
Restart=on-failure
RestartSec=10
KillSignal=SIGINT
TimeoutStopSec=120
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Recargar systemd:**
```bash
systemctl daemon-reload
```

## 11. Habilitar e iniciar el servicio

```bash
systemctl enable --now valheim
```

Esto habilita el arranque automático del servidor junto con el sistema, y lo inicia de inmediato.

## 12. Verificar que arrancó correctamente

```bash
systemctl status valheim
journalctl -u valheim -f
```

En los logs, algunos mensajes son normales y esperables aunque parezcan errores:

| Mensaje | Explicación |
|---|---|
| `DllNotFoundException` (PartyCSharpSDK) | Benigno — librería de voice chat de Windows que no existe en Linux, no afecta el funcionamiento |
| `Failed to place all <Estructura>, placed X out of Y` | Normal — el generador de mundo optimizando ubicación de estructuras, no indica un problema |

La generación inicial del mundo puede tardar 60-90 segundos. Buscá la línea `Opened Steam server` y `Game server connected` como confirmación de que terminó de inicializar y ya acepta conexiones.

## 13. Probar el ciclo de reinicio

```bash
systemctl stop valheim
systemctl start valheim
journalctl -u valheim -f
```

Confirmar que el servicio vuelve a levantar sin errores y sin pérdida de datos del mundo.

---

# Parte 3 — Backups, resiliencia y conectividad

## 14. Configurar backups nativos de Valheim

**Editar el script de arranque** para agregar los parámetros de guardado y backup automático del propio Valheim:

```bash
nano /opt/valheim-server/start_valheim.sh
```

Agregar estos flags al comando `exec` (cuidado con la barra invertida `\` al final de cada línea, incluida la última antes del siguiente flag):

```bash
    -saveinterval 1800 \
    -backups 4 \
    -backupshort 7200 \
    -backuplong 43200
```

| Flag | Significado |
|---|---|
| `-saveinterval 1800` | Guarda el mundo cada 1800 s (30 min) |
| `-backups 4` | Mantiene 4 backups "long" antes de rotar/borrar |
| `-backupshort 7200` | Backup corto cada 7200 s (2 h) |
| `-backuplong 43200` | Backup largo cada 43200 s (12 h) |

**Verificar sintaxis antes de reiniciar:**
```bash
bash -n /opt/valheim-server/start_valheim.sh
```

## 15. Reiniciar y comprobar backups

```bash
systemctl restart valheim
```

> ⚠️ **Nota**: aunque se configuró `-savedir "/srv/valheim/worlds"`, Valheim crea automáticamente una subcarpeta `worlds_local` dentro de esa ruta y **siempre** guarda ahí (comportamiento fijo del binario, no configurable). La ruta real de mundo y backups nativos termina siendo:
> ```
> /srv/valheim/worlds/worlds_local/
> ```

## 16. Resolver el bug de conexión de `-crossplay`

### Síntoma
El servicio queda `active (running)`, pero los jugadores no pueden conectarse. En los logs aparece un loop repetido cada 30 segundos:

```
PlayFab reconnect server 'NOMBRE_SERVER'
Server 'NOMBRE_SERVER' begin PlayFab create and join network for server
```

### Diagnóstico
Verificar qué puertos UDP están realmente abiertos:

```bash
ss -ulnp
```

Si aparece el puerto de consulta (`2457`) pero **no** el puerto de juego (`2456`), el servidor nunca terminó de inicializar la capa de red — se quedó atascado esperando completar el registro en PlayFab, necesario para el modo `-crossplay`. Es un problema conocido y documentado en servidores Linux con esta opción activada.

### Solución
Quitar el flag `-crossplay` del script de arranque:

```bash
nano /opt/valheim-server/start_valheim.sh
```

El script final, sin crossplay, con los backups nativos y con soporte de modificadores por mundo, queda así:

```bash
#!/bin/bash
export LD_LIBRARY_PATH="./linux64:${LD_LIBRARY_PATH}"
export SteamAppId=892970

SERVER_NAME="NOMBRE_SERVER"
WORLD_NAME="NOMBRE_MUNDO"
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
```

> ⚠️ **Nota**: si copiaste el bloque de arriba tal cual, reemplazá `NOMBRE_SERVER` y `NOMBRE_MUNDO` por los valores reales de tu servidor. Confirmá que no quedó ningún placeholder sin reemplazar:
> ```bash
> grep -E "NOMBRE_MUNDO|NOMBRE_SERVER" /opt/valheim-server/start_valheim.sh
> ```
> Si no devuelve nada, estás bien. Si devuelve algo, Valheim va a generar un mundo nuevo vacío con ese nombre literal en vez de cargar el tuyo.

**Reiniciar y confirmar que ahora sí abre el puerto de juego:**
```bash
systemctl restart valheim
sleep 90
ss -ulnp
```

Debería aparecer `*:2456` en el listado. Buscar en los logs la línea `Opened Steam server` como confirmación.

> ⚠️ **Nota**: al sacar `-crossplay`, el servidor queda accesible solo para jugadores de PC vía Steam (conexión directa por IP o browser de servidores). Si en el futuro se necesita soporte para consolas/Game Pass, hay que investigar más a fondo el problema de PlayFab en Linux — no tiene una solución 100% confiable documentada al momento de esta guía.

## 17. Verificar los backups generados

```bash
ls -la /srv/valheim/worlds/worlds_local/
```

Deberían aparecer, además de los archivos activos del mundo (`NOMBRE_MUNDO.db` / `.fwl`), backups con el formato:

```
NOMBRE_MUNDO_backup_auto-YYYYMMDDHHMMSS.db
NOMBRE_MUNDO_backup_auto-YYYYMMDDHHMMSS.fwl
```

## 18. Configurar backup externo manual con FileZilla

Para no depender únicamente del disco del VPS, se descarga una copia periódica a una máquina externa vía SFTP.

**Datos de conexión en FileZilla** (Archivo → Administrador de sitios → Nuevo sitio, protocolo SFTP):

| Campo | Valor |
|---|---|
| Servidor | `sftp://23.175.40.29` (o el hostname) |
| Usuario | usuario SSH habitual |
| Autenticación | contraseña o archivo de clave privada |
| Puerto | `22` |

**Carpeta a descargar:**
```
/srv/valheim/worlds/worlds_local/
```

Descargar la carpeta completa a la PC local (por ejemplo, en una carpeta con fecha) antes de reinicios importantes del VPS, actualizaciones, o al menos una vez por semana con uso regular.

## 19. Probar la restauración de un backup

Antes de confiar en los backups, se valida que el proceso de restauración funcione:

```bash
systemctl stop valheim
cd /srv/valheim/worlds/worlds_local/

# Resguardo temporal extra (opcional, por seguridad)
mkdir -p /tmp/valheim_test_restore
cp NOMBRE_MUNDO.db NOMBRE_MUNDO.fwl /tmp/valheim_test_restore/

# Simular pérdida (renombrar, no borrar)
mv NOMBRE_MUNDO.db NOMBRE_MUNDO.db.simulacro_perdido
mv NOMBRE_MUNDO.fwl NOMBRE_MUNDO.fwl.simulacro_perdido

# Restaurar desde un backup automático existente
cp NOMBRE_MUNDO_backup_auto-<TIMESTAMP>.db NOMBRE_MUNDO.db
cp NOMBRE_MUNDO_backup_auto-<TIMESTAMP>.fwl NOMBRE_MUNDO.fwl

systemctl start valheim
sleep 90
journalctl -u valheim -n 20 --no-pager
```

Confirmar en los logs `Load world`, `Opened Steam server` y `Game server connected`, y verificar conectando desde el juego que el mundo restaurado es correcto.

**Limpieza final** una vez confirmado que todo funciona:
```bash
cd /srv/valheim/worlds/worlds_local/
rm NOMBRE_MUNDO.db.simulacro_perdido NOMBRE_MUNDO.fwl.simulacro_perdido
rm -rf /tmp/valheim_test_restore
```

---

# Parte 4 — Administración avanzada con `vhctl`

## 20. Construir la herramienta de gestión `vhctl`

Para simplificar la operación diaria (encender/apagar/reiniciar, backups, manejo de mundos, modificadores, monitoreo), se construyó un script wrapper sobre `systemctl` y las rutas del servidor. Fue creciendo por partes a lo largo de este proyecto; la versión final quedó en 439 líneas.

> 📄 **Archivo completo**: ver [`vhctl.sh`](./vhctl.sh). Estructura general del script:
> - Variables globales y mapa de modificadores válidos (`VALID_MODIFIERS`)
> - Funciones internas: `require_root`, `get_world_name`, `set_world_name`, `world_exists`, `do_backup`
> - Comandos generales: `cmd_on`, `cmd_off`, `cmd_reset`, `cmd_status`, `cmd_update`, `cmd_password`, `cmd_monitor`, `cmd_players`, `cmd_gitsync`, `cmd_help`
> - Comandos de mundos: `cmd_worlds_list`, `cmd_worlds_create`, `cmd_worlds_switch`, `cmd_worlds_delete`, `cmd_worlds_modifiers`
> - Dispatcher final (`case "${1:-}"`) que enruta cada subcomando

### Crear el archivo
```bash
nano /usr/local/bin/vhctl
```
Pegar el contenido completo de [`vhctl.sh`](./vhctl.sh).

### Permisos y verificación
```bash
chmod +x /usr/local/bin/vhctl
bash -n /usr/local/bin/vhctl
```

### Uso

```bash
vhctl on                       # enciende el servidor
vhctl off                      # backup + apaga
vhctl reset                    # backup + reinicia
vhctl status                   # estado del servicio y mundo activo
vhctl backup                   # backup manual on-demand
vhctl backups                  # lista los backups de vhctl guardados (nombre, tamaño y total)
vhctl update                   # consulta si hay actualización del juego y pregunta si aplicarla
vhctl password <nueva_pass>    # cambia la contraseña del mundo (pregunta si reiniciar para aplicarla)
vhctl monitor                  # muestra el historial de caídas/recuperaciones detectadas
vhctl players                  # jugadores conectados ahora + actividad reciente por logs
vhctl players last              # último acceso registrado de cada jugador
vhctl gitsync [mensaje]        # copia vhctl y compañía al repo de config-backup y commitea si hay cambios
vhctl help                     # lista todos los comandos disponibles con su descripción
vhctl worlds list              # lista mundos disponibles
vhctl worlds create <nombre> [clave=valor ...]   # crea un mundo (con modificadores opcionales desde la generación)
vhctl worlds switch <nombre>   # cambia de mundo activo (con backup previo)
vhctl worlds delete <nombre> --confirm           # borra un mundo (no permite borrar el activo; backup de seguridad antes)
vhctl worlds modifiers <nombre>                  # ver modificadores configurados
vhctl worlds modifiers <nombre> set clave=valor ...   # configurar modificadores (aplican con un reinicio, aunque el mundo ya exista)
```

Los backups de `vhctl` se guardan comprimidos en `/srv/valheim/worlds/vhctl_backups/`, separados de los backups nativos de Valheim, con retención de los últimos 5.

> ⚠️ **Nota**: no existe forma de especificar un seed por línea de comandos en el servidor dedicado — el seed se define únicamente al crear el mundo desde el cliente del juego. Por eso `worlds create` genera el mundo con seed aleatorio; para usar un seed específico hay que crear el mundo en un cliente local y subir los archivos `.db`/`.fwl` manualmente a `worlds_local/` con el nombre correspondiente.

## 21. Habilitar sudo sin contraseña para `vhctl`

Para poder ejecutar `sudo vhctl ...` con el usuario `valheim` sin que pida contraseña, sin otorgar sudo completo a ese usuario:

### Crear la regla
```bash
visudo -f /etc/sudoers.d/vhctl
```

Contenido (una sola línea):
```
valheim ALL=(root) NOPASSWD: /usr/local/bin/vhctl
```

**Ajustar permisos del archivo:**
```bash
chmod 440 /etc/sudoers.d/vhctl
```

### Verificar
```bash
su - valheim
sudo vhctl status
```

No debería pedir contraseña, y el usuario `valheim` sigue sin tener sudo para ningún otro comando.

## 22. Versionar la configuración con git

Después de varios incidentes por ediciones manuales que rompieron el script (una barra invertida faltante, una variable no definida, un placeholder sin reemplazar), conviene versionar los archivos de configuración clave para poder comparar y revertir cambios sin reconstruir todo a mano. No hace falta GitHub ni ningún servicio externo — el repo vive únicamente en el VPS (aunque si en algún momento se sube a un remoto, el diseño de este paso ya contempla esa transición, ver la nota de seguridad al final).

### Inicializar el repositorio
```bash
sudo mkdir -p /srv/valheim/config-backup
cd /srv/valheim/config-backup
sudo git init
sudo git config user.email "admin@mustachent.local"
sudo git config user.name "vhctl-admin"
```

### Primer commit manual (una sola vez)
```bash
sudo cp /usr/local/bin/vhctl ./vhctl
sudo cp /opt/valheim-server/start_valheim.sh ./start_valheim.sh
sudo cp /etc/systemd/system/valheim.service ./valheim.service
sudo cp /etc/sudoers.d/vhctl ./sudoers-vhctl
echo "VALHEIM_PASSWORD=<definida en /etc/valheim-server.env, no versionada por seguridad>" | sudo tee ./valheim-server.env.example

sudo git add .
sudo git commit -m "Snapshot inicial: vhctl, start_valheim.sh, systemd unit, sudoers"
```

> ⚠️ **Nota**: no se versiona `/etc/valheim-server.env` (contiene la contraseña en texto plano) — se deja solo el `.example` de arriba como recordatorio de qué variable necesita.

### Automatizar los commits siguientes con `vhctl gitsync`

A partir de acá, en vez de repetir `cp` + `git add` + `git commit` a mano cada vez que se edita `vhctl` o cualquier otro archivo de configuración, `vhctl` incluye un subcomando que hace todo el flujo de una vez: copia todos los archivos versionados (según la lista `CONFIG_FILES` dentro del propio script), la carpeta de modificadores, y una referencia del crontab actual; después detecta si hubo cambios reales y commitea solo en ese caso.

```bash
sudo vhctl gitsync "Descripción corta del cambio"
```

Si no se pasa un mensaje, usa uno automático con fecha y hora. Si no hay cambios respecto al último commit, lo avisa y no genera un commit vacío.

La primera vez que se corre, también crea un `.gitignore` de seguridad en `config-backup` (patrones tipo `*.env`, `*secret*`, `*password*`, `*.key`, `*.pem`) — una red de seguridad extra para el día en que este repo se suba a un remoto como GitHub, por si alguna vez se llega a copiar sin querer algo sensible ahí adentro.

> ⚠️ **Nota**: `git status` solo compara las copias *dentro* de `config-backup` contra el último commit — no las compara contra el archivo real y actual del sistema. Por eso `gitsync` siempre copia primero y recién después mira si hay diferencias; nunca hay que confiar en `git status` solo, sin haber corrido antes el `cp` (o `gitsync`, que ya lo hace).

### Antes de subir el repo a un remoto (GitHub u otro)

Verificar que nunca se haya colado un secreto real en el historial:
```bash
cd /srv/valheim/config-backup
git log --all -p | grep -i "VALHEIM_PASSWORD="
```
Solo debería aparecer la línea del `.example` (placeholder) y las líneas de código que *manejan* la variable (`grep`, `sed`, `echo` dentro de `cmd_password`) — nunca un valor real. Si aparece algo real, hay que reescribir el historial antes de hacer público el repo (`git filter-branch` o similar no alcanza con un commit nuevo que borre el archivo).

### Comandos útiles para revisar el historial
```bash
sudo git log --oneline              # ver todos los commits
sudo git diff HEAD~1 vhctl          # ver qué cambió en el último commit
sudo git show HEAD~2:vhctl > /tmp/version_vieja.sh   # recuperar una versión anterior sin perder la actual
```

## 23. Configurar monitorización básica

Un healthcheck simple que corre cada 5 minutos vía `cron`, y solo escribe en el log cuando **cambia** el estado del servicio (arriba → abajo, o abajo → arriba). Así el log queda como un historial de incidentes, no un chorro constante de líneas repetidas. Se eligió este enfoque (log local, sin webhooks a Discord/Telegram/email) por simplicidad.

### Crear el script de healthcheck
```bash
sudo nano /usr/local/bin/valheim-healthcheck.sh
```

Contenido:

```bash
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
```

**Permisos y validación:**
```bash
sudo chmod +x /usr/local/bin/valheim-healthcheck.sh
sudo bash -n /usr/local/bin/valheim-healthcheck.sh
sudo touch /var/log/valheim-monitor.log
sudo chmod 644 /var/log/valheim-monitor.log
```

### Programar con cron
(cada 5 minutos, como root)
```bash
sudo crontab -e
```

Agregar esta línea:
```
*/5 * * * * /usr/local/bin/valheim-healthcheck.sh
```

### Ver el historial
```bash
sudo vhctl monitor
```
O directamente:
```bash
sudo tail -f /var/log/valheim-monitor.log
```

### Probar que funciona
```bash
sudo systemctl stop valheim
sleep 300   # esperar a que corra el próximo chequeo de cron (hasta 5 min)
sudo vhctl monitor
sudo vhctl on
sleep 300
sudo vhctl monitor
```

Deberían aparecer dos líneas nuevas: una marcando `DOWN` y otra marcando `UP` de vuelta.

No te olvides de sumar el script nuevo al repo de git:
```bash
sudo vhctl gitsync "Agregar monitorización con healthcheck y cron"
```

## 24. Configurar modificadores de mundo

Valheim permite ajustar varios parámetros de comportamiento del juego con flags `-modifier <clave> <valor>`. **A diferencia del seed** (que sí queda fijo para siempre desde el momento en que se genera el mapa), estos modificadores no tocan el terreno — son reglas de comportamiento que el servidor vuelve a leer **cada vez que arranca**. Eso significa que se pueden cambiar en cualquier momento, incluso en un mundo que ya está en uso hace rato: solo hace falta reiniciar el servidor para que tomen efecto. Confirmado en la práctica: agregar `-modifier resources <valor>` a un mundo ya existente y reiniciar el servicio aplicó el cambio correctamente.

### Modificadores disponibles

| Modificador | Función | Valores posibles |
|---|:---:|---|
| `combat` | Dificultad del combate | veryeasy, easy, normal, hard, veryhard |
| `deathpenalty` | Penalización al morir | casual, veryeasy, easy, normal, hard, hardcore |
| `resources` | Tasa de recursos/drop | muchless, less, normal, more, muchmore, most |
| `raids` | Frecuencia de invasiones a la base | none, muchless, less, normal, more, muchmore |
| `portals` | Restricción de portales | casual (teletransporta todo), normal, hard (sin metales), veryhard (desactiva portales) |
| `playerevents` | Eventos basados en jugadores | true, false |
| `passivemobs` | Enemigos pasivos | true, false |
| `nobuildcost` | Construcción gratuita | true, false |

### Cómo funciona en `vhctl`

Los modificadores se guardan **por mundo**, en `/srv/valheim/worlds/modifiers/<nombre>.conf`. El script de arranque (paso 16) los lee automáticamente en cada arranque según cuál sea el mundo activo en ese momento, así que cada mundo puede tener su propia combinación sin pisar la de otro, y los cambios se pueden aplicar cuando quieras con un reinicio.

**Crear un mundo con modificadores desde el arranque:**
```bash
sudo vhctl worlds create Hardcore combat=veryhard deathpenalty=hardcore resources=less raids=more
```

**Ver los modificadores configurados para un mundo:**
```bash
sudo vhctl worlds modifiers Hardcore
```

**Configurar o cambiar modificadores en cualquier momento:**
```bash
sudo vhctl worlds modifiers Hardcore set portals=hard nobuildcost=false
```

Si el mundo que estás modificando es el que está activo ahora mismo, `vhctl` pregunta si querés reiniciar el servidor ya mismo para aplicar el cambio (con backup automático antes, igual que `password` y `update`). Si es otro mundo, avisa que se va a aplicar la próxima vez que ese mundo esté activo y el servidor se reinicie.

`vhctl` valida automáticamente que la clave y el valor sean válidos antes de guardar nada — si te equivocás de nombre o valor, lo rechaza con la lista de opciones válidas.

No te olvides de sumar la carpeta de modificadores al backup de git:
```bash
sudo vhctl gitsync "Agregar configuración de modificadores por mundo"
```

## 25. Configurar la zona horaria del servidor

Por defecto, el VPS queda en `UTC`. Todos los timestamps del sistema (`journalctl`, `vhctl monitor`, `vhctl players last`) se muestran en esa zona, lo que puede generar confusión al comparar contra la hora real de quien administra el servidor.

### Verificar la zona horaria actual
```bash
date
timedatectl status
```

### Cambiarla a la zona horaria propia
```bash
sudo timedatectl set-timezone America/Argentina/Buenos_Aires
```

(reemplazar por la zona horaria que corresponda — `timedatectl list-timezones` para ver todas las opciones disponibles)

### Confirmar el cambio
```bash
date
timedatectl status
```

Debería mostrar la zona horaria nueva y la hora coincidiendo con la hora real.

> ⚠️ **Nota**: no hace falta modificar ningún script después de este cambio. Tanto `journalctl` como los scripts de Python de `vhctl` (`valheim-players-query.py`, `valheim-track-players.py`) usan la hora del sistema automáticamente — apenas se cambia el timezone, todo pasa a mostrarse en la hora local sin tocar código. Las entradas que ya estaban guardadas antes del cambio (por ejemplo, en `/var/lib/valheim/players-lastseen.json`) van a quedar con el offset viejo respecto a las nuevas; no es un error, es solo una diferencia de las entradas históricas.

## 26. Ver jugadores conectados y su último acceso

Valheim expone un puerto de consulta estilo Steam (`2457`, el mismo `SERVER_PORT + 1` que ya está abierto en el firewall) que responde al protocolo `A2S_INFO` — de ahí se obtiene el conteo de jugadores de forma confiable. **Importante**: Valheim **no** implementa `A2S_PLAYER` (la variante del protocolo que da nombres individuales), así que los nombres y la actividad reciente se obtienen de otra fuente: el log del servidor.

Cada vez que un jugador se conecta o reaparece después de morir, el log registra una línea `Got character ZDOID from <nombre> :`. No hace falta distinguir entre "se conectó" y "reapareció" para este propósito — cualquiera de los dos casos confirma que esa persona está activa en ese momento.

### Instalar la dependencia
```bash
sudo apt-get update
sudo apt install -y python3-pip
sudo pip3 install python-a2s --break-system-packages
```
Verificar:
```bash
python3 -c "import a2s; print('OK')"
```

> ⚠️ **Nota**: si `apt install` falla con un error `404 Not Found` sobre paquetes de `python3.12-dev`, es un índice desactualizado del mirror de seguridad de Ubuntu, no algo de esta configuración. Se resuelve con `sudo apt-get update` (o `--fix-missing`) antes de reintentar.

### Instalar los scripts

> 📄 **Archivos completos**: ver [`valheim-players-query.py`](./valheim-players-query.py) y [`valheim-track-players.py`](./valheim-track-players.py).
>
> - `valheim-players-query.py`: consulta `a2s.info()` para el conteo en vivo, y lee el archivo de estado para mostrar nombres con actividad en los últimos 10 minutos.
> - `valheim-track-players.py`: pensado para correr por cron cada 5 minutos. Revisa los últimos 6 minutos del log (`journalctl -u valheim --since "6 min ago"`), extrae los nombres de las líneas `Got character ZDOID from`, y actualiza `/var/lib/valheim/players-lastseen.json` con la hora de la última vez que se vio a cada uno.

```bash
sudo nano /usr/local/bin/valheim-players-query.py
sudo nano /usr/local/bin/valheim-track-players.py
sudo chmod +x /usr/local/bin/valheim-players-query.py /usr/local/bin/valheim-track-players.py
```

### Programar el tracker con cron
(mismo patrón que el healthcheck del paso 23; se puede agregar como línea adicional al mismo crontab)
```bash
sudo crontab -e
```
```
*/5 * * * * /usr/local/bin/valheim-track-players.py
```

### Uso
```bash
vhctl players         # jugadores conectados ahora (conteo confiable) + nombres con actividad reciente (heurística de logs)
vhctl players last     # último acceso registrado de cada jugador, ordenado del más reciente al más antiguo
```

`vhctl players` también muestra el mundo activo real (leído de `start_valheim.sh` vía `get_world_name`), no el que reporta el campo `map` de la consulta Steam — ese campo tiene un comportamiento conocido en Valheim de devolver el nombre del servidor en vez del mundo.

No te olvides de sumar los scripts nuevos al repo de git:
```bash
sudo vhctl gitsync "Agregar vhctl players (jugadores conectados y último acceso)"
```

---

### Próximos pasos (no incluidos en esta guía)

- Mejorar seguridad SSH (deshabilitar login por contraseña, revisar acceso root directo, fail2ban).
- Documentación final y automatizaciones adicionales.
- Soporte de mods (pendiente de evaluar).

### 🗒️ Changelog de la guía

- **Bug de `-crossplay`**: el flag bloqueaba la inicialización completa del server en Linux (loop de `PlayFab reconnect`, puerto de juego nunca se abría). Se resolvió quitándolo (paso 16).
- **Comentario `#-crossplay` mal puesto**: al intentar desactivar el flag comentándolo en vez de borrarlo, la continuación de línea (`\`) hizo que el `#` comentara también todos los flags siguientes (`-savedir`, backups, `-public`). El mundo terminó guardándose en la ruta default de Valheim en vez de `/srv/valheim/worlds`. Se resolvió borrando la línea entera y moviendo los archivos a la ruta correcta.
- **Formato de mundo por carpetas (Valheim 1.0+)**: se descubrió que los mundos nuevos usan una carpeta con archivos `.chunk`/`.db2`/`.fwl2` en vez de los `.db`/`.fwl` sueltos del formato clásico. `vhctl` se actualizó (`world_exists`, `do_backup`, `worlds list/switch/delete`) para reconocer ambos formatos.
- **Contraseña visible en `vhctl status`**: la salida de `systemctl status` mostraba la contraseña del mundo en texto plano como argumento del proceso. Se agregó un `sed` que la enmascara en la salida de `vhctl status` (aunque sigue siendo visible vía `ps aux` para cualquiera con shell en el servidor — limitación del propio Valheim, no de `vhctl`).
- **Placeholder `NOMBRE_MUNDO` sin reemplazar**: al copiar un bloque de la guía sin reemplazar el placeholder, Valheim generó un mundo nuevo vacío con ese nombre literal. Se resolvió restaurando `start_valheim.sh` desde un backup previo. Se agregó la advertencia de verificación con `grep` en el paso 16.
- **Modificadores de mundo — corrección importante**: se documentó inicialmente que los modificadores solo aplicaban en la generación inicial de un mundo (como el seed). Se comprobó empíricamente que esto es incorrecto para estos modificadores en particular — son reglas de runtime que se vuelven a leer en cada arranque, y aplican a mundos existentes con un simple reinicio. `vhctl worlds modifiers` se corrigió para ofrecer reiniciar el servidor al aplicar cambios, en vez de advertir que no tendrían efecto.
- **Repo de git desactualizado sin aviso**: `git status` solo compara contra las copias locales dentro de `config-backup`, no contra los archivos reales del sistema — es posible editar `vhctl` o `start_valheim.sh` y que el repo diga "nothing to commit" simplemente porque nunca se volvió a copiar el archivo actualizado. Documentado como nota en el paso 22.
- **`A2S_PLAYER` no soportado por Valheim**: el primer intento de `vhctl players` usaba `a2s.players()` para obtener nombres individuales vía consulta Steam, pero Valheim no implementa esa parte del protocolo (solo `A2S_INFO`). Se corrigió reemplazando la fuente de nombres por un tracker basado en logs (líneas `Got character ZDOID from`), manteniendo `a2s.info()` únicamente para el conteo, que sí es confiable.
- **Campo "mundo" incorrecto en la consulta Steam**: `a2s.info()` devuelve el nombre del servidor (`-name`) en el campo `map_name`, no el mundo real (`-world`). Se corrigió mostrando el mundo real vía `get_world_name()` de `vhctl` en vez de confiar en ese campo.
- **Comentarios agregados a `vhctl`**: con el script creciendo (más de 600 líneas), se agregó un comentario corto arriba de cada función explicando qué hace, más comentarios inline en las partes que ya generaron confusión real (formatos de mundo, modificadores, por qué no se usa `a2s.players()`).
- **`vhctl gitsync`**: automatiza la copia de todos los archivos versionados + commit, reemplazando la secuencia manual de `cp` + `git add` + `git commit` del paso 22. Se agregó pensando en la transición a un repo remoto (GitHub), con un `.gitignore` de seguridad generado automáticamente en la primera corrida.
