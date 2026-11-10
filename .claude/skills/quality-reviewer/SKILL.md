---
name: quality-reviewer
description: "Control de calidad antes de entregar: mide imagen y audio, separa defectos bloqueantes de preferencias estéticas, respeta lo declarado como intencionado y obliga a mirar los fotogramas. Usar siempre antes de entregar un vídeo o una presentación."
---

# Control de calidad

```bash
python -m universal.cli qc --video out/x.mp4 --frames out/x-pruebas --project out/project.json --subtitles out/x.srt --styleframe estilo.png@3
```
Mide: códec, píxeles, resolución, cadencia, duración, errores de decodificación, negros, imágenes congeladas, cortes, movimiento, LUFS, picos, silencios, final cortado, subtítulos y distancia a un fotograma de estilo. Crea `planche.jpg` y `zones-sures.jpg`.

| Campo | Significado |
|---|---|
| `blocking` | Defecto real: corregir antes de entregar |
| `warnings` | Revisar y decidir |
| `declared` | Declarado en `quality.exceptions`: correcto |
| `aesthetic` | Señal para el ojo, no un fallo |

Una secuencia negra, silenciosa, lenta o sin CTA puede ser correcta: declárala en vez de «arreglarla».

## Obligatorio: mirar
Abre `planche.jpg` y `zones-sures.jpg`, **escucha el audio**. El control técnico no detecta un subtítulo repetido ni una escena desfasada de la voz: en este kit pasó y solo se vio mirando.

Revisa: texto dentro de las zonas seguras, cifras iguales a la fuente, personaje coherente entre planos, cursor sobre el elemento nombrado, nada cortado.

## Después
`motion-memoria`, parte B. Las páginas HTML entregadas pasan además un control de diseño automático (`modules/design-check`): sus alertas salen en el informe. Solo aconseja. Juzga cada una mirando la página: una parte es cuestión de gusto y algunas son falsas, por ejemplo un bloque con capas que tienen su propio margen o un texto sobre un fondo animado. No ve lo que se dibuja en un canvas, así que no dice nada de las páginas de película. `run` escribe solo el historial en `perfil/`; `template/scripts/control-calidad.ps1` sigue disponible y también escribe el historial en `perfil/calidad.jsonl`.
