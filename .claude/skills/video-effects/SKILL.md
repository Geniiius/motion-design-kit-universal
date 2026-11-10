---
name: video-effects
description: "Efectos sobre un vídeo de una persona que habla a cámara: texto detrás de la cabeza, seguimiento de la cara, foco, tarjetas alrededor, zoom a una palabra. 51 efectos locales. Usar cuando la ficha indica el motor video-effects, o cuando piden un efecto por su nombre (orbit, spotlight, backdrop-word, glass-widgets…), o algo «detrás de mi cabeza», «que siga mi cara»."
---

# Efectos sobre una persona filmada

Todo es local: el vídeo no sale de la máquina. Los modelos de cara y silueta vienen en el kit.

## Antes de empezar

- **Consentimiento**: se sigue y se recorta a una persona real. Confirma que quien aparece está de acuerdo.
- **Módulo**: es una opción gratuita (unos 450 MB, versiones fijadas) que **no se instala sola**. Si falta, pide permiso en una frase y, con su «sí», `python -m universal.cli setup apply --approve effects` (skill `kit-onboarding`).
- **Vídeo**: pensado para vertical, con la persona de frente y una sola persona. En horizontal los 51 efectos funcionan, pero varios títulos y tarjetas se salen del cuadro (por ejemplo `split-headline`, `phone-fan`, `orbit`): mira cada uno antes de entregar.
- Lista con las opciones obligatorias de cada efecto: `presets/video-effects.json`. Tabla completa: `python -m universal.cli effects list`.

## Método

1. **Encontrar el momento.** Si dicen «cuando digo X»: `python -m universal.cli transcribe video.mp4 -o out/<proyecto>/palabras.json --language fr`. Exige la opción «subtítulos automáticos» (345 MB): pregunta en palabras normales y, con su «sí», `setup apply --approve captions`. Sirve para los tiempos: oye mal nombres y homófonos, así que no copies su texto en pantalla sin revisarlo.
2. **Escribir el plan** en `plan.json`. Ventanas cortas: de 1,5 a 4 segundos.
   ```json
   {"effects": [
     {"fx": "orbit", "start": 3.2, "end": 6.0},
     {"fx": "backdrop-word", "start": 14.0, "end": 16.3, "text": "VERANO"}
   ]}
   ```
3. **Comprobar las opciones**: `python -m universal.cli effects check plan.json`.
4. **Mirar antes de renderizar**, en el centro de cada efecto:
   ```bash
   python -m universal.cli effects still video.mp4 --plan plan.json --at 4.5,15.2 -o out/<proyecto>/prueba.png
   ```
   **Abre las imágenes.** Corrige si tapa la cara, se corta o no se lee.
5. **Renderizar**: `python -m universal.cli effects render video.mp4 --plan plan.json -o out/<proyecto>/final.mp4 --profile final`. El audio original se conserva.
6. **Control**: `python -m universal.cli qc --video out/<proyecto>/final.mp4 --frames out/<proyecto>/preuves`, y mira los fotogramas.

## Reglas que no se saltan

- **Ningún dato inventado.** Todo texto, nombre o cifra en pantalla sale del plan y del usuario. Si un efecto pide `to`, `views`, `count` o `total`, esos números tienen que ser reales: pregúntalos. Sin ellos, el efecto se niega a arrancar, y eso es lo correcto.
- **Interfaces de marca.** `comment-box`, `reel-frame`, `tap`, `pastel-word`, `profile-wall`, `place-in-grid` imitan a Instagram, `messages` a iMessage, `apple-toggles` al iPhone. Avisa del riesgo y usa `--interfaces-marques` (o `props.brand_ui_ok` en el manifiesto) solo si el usuario lo acepta.
- **`match-cut`** muestra páginas falsas con texto de relleno: nunca lo presentes como prensa real.
- **Cara no encontrada.** El resultado incluye `tracking` y puede traer un aviso. Si `faces` es bajo, los elementos pueden quedar delante de la persona: revisa antes de entregar y dilo.

## Límites

Son versiones de partida: añaden imagen, no sonido ni subtítulos (para eso, `media-ingestion-and-edit` y `motion-sound-effects`). Probado en un clip sin personas. **El seguimiento de una cara real está sin probar** hasta que alguien aporte un vídeo con consentimiento: dilo si te preguntan.
