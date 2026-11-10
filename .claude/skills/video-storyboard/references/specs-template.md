# Plantilla de especificaciones técnicas

## 0. Ficha
```
Proyecto: [nombre]          Versión: [sobria | audaz]
Formato(s): [9:16 1080×1920 / 1:1 1080×1080 / 16:9 1920×1080]   FPS: 30
Duración total: [s]         Plataforma: [..]
Restricciones de marca: [logo, colores, tipografías, legales]
Motor de producción: [Remotion template | HyperFrames | Prompt Motion]
```

## 1. Línea de tiempo y keyframes (una tabla por escena)

Escena [#] — [nombre] · [inicio]–[fin] s

| Elemento | Propiedad | Keyframes (tiempo local → valor) | Easing | Notas |
|---|---|---|---|---|
| Título | opacity | 0,00 s → 0 · 0,40 s → 1 | ease-out `(.16,1,.3,1)` | stagger 40 ms por palabra |
| Título | translateY | 0,00 s → 40 px · 0,50 s → 0 | spring 180/20 | |
| Título | blur | 0,00 s → 8 px · 0,35 s → 0 | ease-out | |
| Palabra acento | color | 0,60 s → texto · 0,75 s → acento | ease-in-out | énfasis |
| Grupo | salida | [fin −0,30 s] → opacity 0, Y −20 px | ease-in `(.7,0,.84,0)` | salida más rápida que la entrada |

## 2. Transiciones

| De → a | Tipo | Duración | Easing | Detalle |
|---|---|---|---|---|
| 1 → 2 | push vertical | 0,4 s | ease-in-out | la escena 2 empuja desde abajo |
| 2 → 3 | match cut / morph | 0,5 s | spring | el botón se convierte en tarjeta |

## 3. Textos definitivos

| Escena | Texto | Palabra resaltada | Tamaño (px en 1080) | Tiempo en pantalla |
|---|---|---|---|---|

Verificar: ≤ 7 palabras · tiempo ≥ 0,3 s/palabra + 1 s · dentro de las zonas seguras.

## 4. Assets necesarios

| Asset | Formato | Fuente | Estado |
|---|---|---|---|
| Logo | SVG o PNG transparente | cliente | ☐ |
| Capturas de producto | PNG 2x | `npm run capture` (playwright-capture) | ☐ |
| Música | MP3/WAV, [BPM] | librería libre de derechos / ElevenLabs `music` | ☐ |
| SFX | WAV | `motion-sound-effects` / ElevenLabs `sound-effects` | ☐ |
| Voz en off | WAV | ElevenLabs `text-to-speech` | ☐ |
| Tipografías | Google Fonts / archivos de marca | | ☐ |

## 5. Audio

Música a ≈ −14 LUFS (−16 si hay voz), voz por encima con ducking, SFX alineados con las
acciones (clic, aparición, transición). Fade-in 0,5 s / fade-out 1 s.

## 6. Exportación

| Plataforma | Archivo | Especificaciones |
|---|---|---|
| Reels / TikTok / Shorts | `nombre-9x16.mp4` | H.264 High, yuv420p, 30 fps, AAC 48 kHz, faststart, ≤ 90 s |
| Feed | `nombre-1x1.mp4` / `-4x5.mp4` | idem |
| YouTube / web | `nombre-16x9.mp4` | idem, CRF 16–18 |
| Subtítulos | `nombre.srt` | además incrustados en el vídeo |

Comando: `template\scripts\ffmpeg\social-export.ps1 <video> -Platform instagram|tiktok|youtube|linkedin|web`

## 7. Control de calidad antes de entregar

- [ ] Fotogramas clave revisados (hook, cada escena, CTA)
- [ ] Ningún texto fuera de zonas seguras
- [ ] Ningún movimiento lineal no intencionado
- [ ] Audio sin saturación, subtítulos sincronizados
- [ ] Versión sobria y versión audaz entregadas
