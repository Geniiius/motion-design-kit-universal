# Prompt Motion — motor HTML `seek(t)`

Vídeos con el estilo de [prompt-motion.com](https://prompt-motion.com): un archivo HTML por vídeo,
todo calculado a partir del tiempo, renderizado fotograma a fotograma con Playwright y codificado con ffmpeg.

```powershell
cd prompt-motion
start compositions\paper-ui.html                                  # vista previa (espacio = pausa, ← → = fotograma)
node render.mjs compositions/paper-ui.html --stills 0.5,2,4,6     # imágenes de control -> out/
node render.mjs compositions/paper-ui.html                        # MP4 -> out/paper-ui.mp4
node render.mjs compositions/studio-hud.html --audio ..\template\public\audio\musica\pista.mp3
```

| Archivo | Función |
|---|---|
| `engine/core.js` | `PM.spring` (muelle de forma cerrada), `PM.track` (varios objetivos), `PM.keyframes`, `PM.beats(bpm)`, `PM.bezier`, easings, vista previa automática |
| `render.mjs` | Playwright → JPEG → ffmpeg (H.264 yuv420p, faststart), `--audio`, `--from/--to`, `--stills` |
| `compositions/paper-ui.html` | Look **Paper**: botón → loader → check → tarjeta con gráfico → botón, guiado por un cursor, 1080×1080, 8 s, bucle |
| `compositions/studio-hud.html` | Look **Studio HUD**: punto → órbita → destello → tipografía gigante → contador → logo, 1080×1920, 10 s, bucle |

Cada composición tiene un bloque «Campos personalizables» (colores, textos, tiempos clave).
Reglas de estilo y plantillas de prompts: skill `prompt-motion-style`.
