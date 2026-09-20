![valheim-banner.png](https://i.postimg.cc/ht4S1m96/valheim-banner.png)

# ⚔️ Valheim Server Admin — Mustachent

Herramientas y configuración para administrar un servidor dedicado de Valheim en una VPS Ubuntu: `vhctl` (CLI de administración construida a medida), scripts de monitorización/tracking de jugadores, y toda la configuración versionada del servidor.

> Este repo **no** incluye datos del mundo ni la contraseña real del servidor — ver [Seguridad](#-seguridad) más abajo.

---

## 📖 Documentación

| Guía | Para quién |
|---|---|
| [`doc/guia-servidor-valheim.md`](./doc/guia-servidor-valheim.md) | Guía técnica completa: instalación desde cero, cada bug encontrado y su solución, y el diseño de `vhctl` paso a paso |
| [`doc/guia-rapida-admin-valheim.md`](./doc/guia-rapida-admin-valheim.md) | Cheat sheet para administradores del server: comandos de uso diario, modificadores de mundo, troubleshooting |

---

## 📂 Estructura del repo

```
.
├── vhctl                          # CLI principal de administración (on/off/backups/mundos/jugadores/git)
├── start_valheim.sh                # script de arranque del servidor dedicado
├── valheim.service                 # unidad systemd
├── sudoers-vhctl                   # regla sudo sin contraseña, acotada solo a vhctl
├── valheim-healthcheck.sh          # healthcheck de uptime (corre por cron)
├── valheim-players-query.py        # consulta en vivo de jugadores conectados
├── valheim-track-players.py        # tracker de último acceso por jugador (corre por cron)
├── valheim-server.env.example      # variables de entorno necesarias, sin valores reales
├── crontab-root.txt                # referencia del cron configurado en el VPS
├── modifiers/                      # modificadores de dificultad/recursos guardados por mundo
└── doc/
    ├── guia-servidor-valheim.md
    └── guia-rapida-admin-valheim.md
```

---

## ⚙️ `vhctl` — comandos principales

```bash
vhctl on / off / reset            # encender, apagar, reiniciar (con backup automático en off/reset)
vhctl status                      # estado del servicio y mundo activo
vhctl backup / backups            # backup manual / listar backups guardados
vhctl update                      # chequear y aplicar actualizaciones del juego
vhctl password <nueva>            # cambiar la contraseña del mundo
vhctl monitor                     # historial de caídas/recuperaciones
vhctl players / players last      # jugadores conectados ahora / último acceso registrado
vhctl gitsync [mensaje]           # versiona esta config: copia + commit + push a este repo
vhctl worlds list/create/switch/delete/modifiers   # gestión de mundos y sus modificadores
vhctl help                        # lista completa de comandos
```

Detalle completo de cada uno en la [guía técnica](./doc/guia-servidor-valheim.md).

---

## 🔒 Seguridad

- `/etc/valheim-server.env` (contraseña real del mundo) **nunca** se versiona — solo existe `valheim-server.env.example` como referencia de qué variable define.
- `.gitignore` incluye patrones de seguridad (`*.env`, `*secret*`, `*password*`, `*.key`, `*.pem`) como red adicional.
- El historial se auditó antes del primer push para confirmar que no había ningún valor real filtrado.

Si encontrás algo que no debería estar acá, avisá antes de asumir que es seguro.

---

## 🪓 Sobre el proyecto

Server privado de Valheim para un grupo de amigos, administrado con herramientas propias construidas de forma incremental — cada comando de `vhctl` nació de una necesidad real durante la operación del server, documentada con su motivo en el changelog de la guía técnica.
