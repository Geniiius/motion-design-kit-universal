---
name: prompt-motion-style
description: "Crear vídeos de motion design con el estilo de prompt-motion.com (vídeos hechos por Claude, nivel Dribbble / showreel): UI que se transforma bajo un cursor sobre fondo papel gris cálido, HUD de estudio negro y rojo anaranjado, tipografía cinética gigante, partículas, datos que se dibujan, todo al ritmo de un BPM. Usar cuando se quiera este estilo, un showreel, un acabado premium «que no parezca plantilla», una demo de producto animada estilo Dribbble, o se mencione Prompt Motion. Incluye el motor HTML seek(t), 2 composiciones listas, las reglas de estilo y plantillas de prompts."
---

# Estilo Prompt Motion

Motor y ejemplos: `Motion-Design-Kit/prompt-motion/` (ver su `LEEME.md`).

## Método (innegociable)

1. **Un archivo HTML por vídeo** y todo es una **función pura del tiempo**: `window.seek(t)` coloca
   cada elemento en el instante t. Sin transiciones CSS, sin temporizadores, sin estado entre fotogramas.
2. **Springs de forma cerrada** (`PM.spring`, `PM.track`): un valor que cambia de objetivo varias
   veces = suma de un spring por cambio. Overshoot mínimo (`snappy`), `pop` solo para un clic.
3. **Rejilla de tempo**: elegir un BPM (a menudo 120 → 1 tiempo = 0,5 s). Pasa algo **en cada
   tiempo**. Con música (generada con la skill `music` de ElevenLabs o propia): analizar el beat
   (`npx hyperframes beats` o `analyze_song.py` de `claude-motion-design`) y empezar en un tiempo fuerte.
4. **Una sola forma que nunca corta** cuando sea posible: se transforma (tamaño, radio, color)
   mientras su contenido cambia con un desenfoque corto (0,15 s).
5. **Bucle**: el último fotograma = el primero.
6. **Verificar**: `node render.mjs <comp>.html --stills 0.5,2,4,6` → mirar los PNG → corregir →
   solo entonces `node render.mjs <comp>.html`.

## Los dos looks

| | **Paper** (`compositions/paper-ui.html`) | **Studio HUD** (`compositions/studio-hud.html`) |
|---|---|---|
| Fondo | gris cálido `#ECEAE4` | negro `#0A0A0A` |
| Tinta | negro `#111`, tarjetas blancas | blanco roto `#F2F0EA` |
| Acento único | rojo anaranjado `#E8462C` | `#FF4F1F` |
| Tipografía | Geist 600, tracking ajustado | Geist 900 gigante, -0.06em |
| Detalles | cursor que hace clic / arrastra, tooltip, sombras suaves | esquinas de encuadre, etiquetas Geist Mono diminutas, timecode, marcas de progreso, línea de escaneo |
| Temas | UI de producto, móvil, gráficos, código | tipografía cinética, formas, partículas, showreel |

Otras variantes del sitio: *editorial claro* (blanco puro, fotos recortadas, anotaciones
manuscritas azules, flechas), *grabado / collage* (fotos en B/N + elementos pintados),
*3D en tiempo real* (three.js). Siempre: **un** color de acento, **una** familia tipográfica (+ su mono).

## Prohibido (el «look plantilla»)

Easing con rebote exagerado, brillos, degradados en la UI, explosiones de partículas sin
motivo, iconos con grosores distintos, tiempos muertos, todo centrado por defecto, etiquetas
decorativas inútiles, beige «artsy» apagado, más de 2 tipografías, fundidos simples entre
escenas (mejor morph / match cut / push).

## Empezar un vídeo nuevo

1. Copiar la composición más parecida (`paper-ui` o `studio-hud`) en `compositions/`.
2. Cambiar el bloque «Campos personalizables» (colores CSS, textos, `WORDS`, `STAT`, tiempos clave).
3. Escribir la timeline en **tiempos musicales** (`B.beat(n)`) en vez de segundos arbitrarios.
4. Formatos: cambiar `width/height` en `COMP` **y** en el CSS `html, body`
   (1080×1920 Reel, 1080×1350 feed, 1080×1080, 1920×1080).
5. Audio (voz/música de ElevenLabs): `node render.mjs comp.html --audio ..\template\public\audio\musica\pista.mp3`.

Para algo más ambicioso (10+ escenas, remake de un vídeo de referencia, efectos de sonido):
skill `claude-motion-design` (misma filosofía seek(t)). En HyperFrames: skills `motion-graphics`
/ `product-launch-video` con estas mismas reglas de estilo.

## Plantillas de prompts

Prompts estructurados (entradas / dirección / estructura / construcción): `references/prompts.md`.
