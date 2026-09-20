![valheim-banner.png](https://i.postimg.cc/ht4S1m96/valheim-banner.png)

# ⚔️ Guía rápida — Server de Valheim ⚔️

<p>
<span style="background:#8B4513;color:white;padding:5px 10px;border-radius:4px;font-weight:bold;font-family:sans-serif;">VALHEIM SERVER</span>
<span style="background:#1B2838;color:white;padding:5px 10px;border-radius:4px;font-weight:bold;font-family:sans-serif;">STEAM ONLY</span>
<span style="background:#c0392b;color:white;padding:5px 10px;border-radius:4px;font-weight:bold;font-family:sans-serif;">CROSSPLAY: OFF</span>
</p>

> *"Odín os observa, guerrero. Prendé el server, honrá a tus ancestros, y no te olvides de avisar en el grupo antes de reiniciar."* 🪓

📘 *Guía técnica completa, con el detalle de cómo se armó todo esto: [guia-servidor-valheim.md](./guia-servidor-valheim.md)*

---

## 🎮 Acceso rápido

| Dato | Valor |
|---|---|
| 🌐 IP del server | `xx.xxx.xx.xx` |
| 🔌 Puerto | `2456` |
| 🏰 Nombre del server | Buscalo en el browser de servidores de Steam, o agregalo por IP directo |
| 🔒 Contraseña del mundo | Pedísela a quien te pasó esta guía |

> ⚔️ **Nota**: sin crossplay — solo PC vía Steam. Xbox y Game Pass no pueden unirse (por ahora).

---

## 🚢 Conectarse por SSH (para administrar)

```bash
ssh valheim@xx.xxx.xx.xx
```

🔑 *Pedile la contraseña o la clave SSH a quien te pasó esta guía.*

---

## ⚡ Comandos básicos

Todos empiezan con `sudo` y **no** van a pedirte contraseña.

| Ícono | Comando                          | Qué hace                                                                |
| :---: | -------------------------------- | ----------------------------------------------------------------------- |
|  🟢   | `sudo vhctl on`                  | Prende el servidor                                                      |
|  🔴   | `sudo vhctl off`                 | Apaga el servidor *(hace backup automático antes)*                      |
|  🔄   | `sudo vhctl reset`               | Reinicia el servidor *(hace backup automático antes)*                   |
|  📊   | `sudo vhctl status`              | Muestra si está prendido y qué mundo está activo                        |
|  💾   | `sudo vhctl backup`              | Hace un backup manual en cualquier momento                              |
|  📂   | `sudo vhctl backups`             | Lista los backups guardados (nombre y tamaño)                           |
|  ⬆️   | `sudo vhctl update`              | Consulta si hay una actualización del juego y pregunta si aplicarla     |
|  🔑   | `sudo vhctl password NUEVA_PASS` | Cambia la contraseña del mundo *(pregunta si reiniciar para aplicarla)* |
|  📉   | `sudo vhctl monitor`             | Muestra el historial de caídas/recuperaciones del servidor              |
|  👥   | `sudo vhctl players`             | Jugadores conectados ahora + actividad reciente                         |
|  🕐   | `sudo vhctl players last`        | Último acceso registrado de cada jugador                                |
|   ❓   | `sudo vhctl help`                | Lista todos los comandos disponibles, por si te olvidás alguno          |

---

## 🌍 Gestión de mundos

| Ícono | Comando | Qué hace |
|:---:|---|---|
| 📜 | `sudo vhctl worlds list` | Lista los mundos guardados y cuál está activo |
| 🌱 | `sudo vhctl worlds create NOMBRE` | Crea un mundo nuevo *(se genera al prender el server)* |
| 🔀 | `sudo vhctl worlds switch NOMBRE` | Cambia al mundo indicado *(reinicia el server)* |
| 🪦 | `sudo vhctl worlds delete NOMBRE --confirm` | Borra un mundo *(no deja borrar el activo)* |
| 🎚️ | `sudo vhctl worlds modifiers NOMBRE` | Ver los modificadores (dificultad, recursos, etc.) de un mundo |
| ⚙️ | `sudo vhctl worlds modifiers NOMBRE set clave=valor` | Configurar modificadores *(aplican con un reinicio, aunque el mundo ya exista)* |

---

## 🎚️ Modificadores disponibles

Usalos con `vhctl worlds modifiers NOMBRE set clave=valor` (podés combinar varios en el mismo comando).

| Modificador | Función | Valores posibles |
|---|---|---|
| `combat` | ⚔️ Dificultad del combate | `veryeasy`, `easy`, `normal`, `hard`, `veryhard` |
| `deathpenalty` | 💀 Penalización al morir | `casual`, `veryeasy`, `easy`, `normal`, `hard`, `hardcore` |
| `resources` | 🪵 Tasa de recursos/drop | `muchless`, `less`, `normal`, `more`, `muchmore`, `most` |
| `raids` | 🔥 Frecuencia de invasiones a la base | `none`, `muchless`, `less`, `normal`, `more`, `muchmore` |
| `portals` | 🌀 Restricción de portales | `casual` (teletransporta todo), `normal`, `hard` (sin metales), `veryhard` (desactiva portales) |
| `playerevents` | 🎉 Eventos basados en jugadores | `true`, `false` |
| `passivemobs` | 🐑 Enemigos pasivos | `true`, `false` |
| `nobuildcost` | 🏗️ Construcción gratuita | `true`, `false` |

**Ejemplo:**
```bash
sudo vhctl worlds modifiers Milfheim set combat=hard raids=more resources=less
```

> ⚠️ **Nota**: si escribís mal una clave o un valor, `vhctl` te lo va a rechazar mostrando las opciones válidas — no hay riesgo de romper nada por un typo.

---

## ⚠️ Reglas del clan

- 📢 **Avisá en el grupo** antes de apagar, reiniciar o cambiar de mundo — desconecta a todos los que estén jugando.
- 🛡️ **No hace falta backupear manualmente** salvo que quieras uno puntual antes de algo importante — los automáticos ya están configurados.
- 📋 **Revisá `vhctl status` antes de tocar nada** si algo se ve raro, no asumas.

---

## 🚨 Si algo falla

1. Corré `sudo vhctl status` — confirmá si el servicio dice `active (running)` o no.
2. Corré `sudo vhctl monitor` — te muestra si hubo caídas recientes registradas.
3. Si el servicio está caído y no sabés por qué, **no intentes arreglarlo por tu cuenta** — avisale al admin. Algunos problemas (firewall, puertos, configuración del script) necesitan revisión más a fondo y tocar lo equivocado puede complicar más las cosas.
4. Si necesitás los detalles técnicos de cómo se armó algo (por qué un comando hace lo que hace, cómo se resolvió un bug pasado), están en la [guía completa](./guia-servidor-valheim.md).

---

<div align="center">

**🪓 ¡Que Odín guíe vuestras hachas! 🪓**

</div>
