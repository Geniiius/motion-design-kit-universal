# Asistente del kit: mantenimiento

Misma regla de oro: nada se reinstala, se borra ni se actualiza sin un «sí» para ese elemento.

## 4. Reparar

```bash
python -m universal.cli repair                      # dice qué falla y qué lo arreglaría. No toca nada
python -m universal.cli repair --approve <id>       # reinstala solo eso, en la carpeta del kit
python -m universal.cli setup verify --deep
```
Explica cada `fix`, pide permiso, repara lo aceptado y vuelve a comprobar. Una herramienta del equipo nunca se reinstala desde aquí: si falta, se propone como en el primer arranque. Diagnóstico completo del equipo: `python -m universal.cli doctor`.

## 5. Desinstalar

```bash
python -m universal.cli uninstall                   # lista y tamaños. No borra nada
python -m universal.cli uninstall --approve <grupo>
```
- `removable`: lo que el kit descargó en su carpeta (motores, opciones, modelos). Se puede volver a instalar.
- `kept`: **su perfil, sus vídeos y sus ajustes. El kit nunca los borra.** Para borrarlo todo, la persona elimina ella misma la carpeta del kit.
- `outside_the_kit`: lo que vive fuera (navegadores de render, herramientas instaladas por el kit, la clave de ElevenLabs). Se explica cómo quitarlo; no se quita solo, porque otros programas pueden usarlo.

## 6. ¿Está al día?

```bash
python -m universal.cli updates                     # consulta los registros públicos; --offline no consulta nada
```
Compara las versiones fijadas con las últimas publicadas. **No actualiza nada**: las versiones del kit están fijadas y auditadas, y una más reciente se prueba antes de adoptarla. Di lo que hay y que el kit se actualiza cambiando su carpeta por una versión nueva, copiando `perfil/`, `out/` y `kit.config.local.json`.

## 7. Dónde está cada cosa

| Archivo | Qué guarda | ¿Se comparte? |
|---|---|---|
| `kit.config.json` | Ajustes de fábrica | Sí, viene con el kit |
| `kit.config.local.json` | Lo que esta persona ha cambiado | No |
| `kit-state.json` | Estado de la instalación en este equipo: acuerdos dados, pasos hechos, último informe | No |
| `logs/` | Registro técnico, sin claves, nombres ni carpeta personal. `logs/dernier-rapport.md` es el último informe | No |

Últimos eventos: `python -m universal.cli logs`.
