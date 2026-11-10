---
name: film-styles
description: "Películas escritas enteramente en código en uno de 66 estilos con nombre: acuarela, óleo, ukiyo-e, risografía, grabado, tinta china, vidriera, pixel art, anime de los 80, cine mudo, plano de metro, investigación visual… Usar cuando la ficha indica el motor film-style, o cuando piden un estilo así, o una película animada sin plantilla, con música y sonido propios."
---

# Películas en un estilo con nombre

Un estilo es una **receta, no una plantilla**: define el aspecto, el color, la cámara y el sonido. La historia, las escenas y el código los escribes tú para este tema. Cuenta **de 30 a 60 minutos y bastantes tokens** para una película completa: avísalo. Para algo rápido, los motores `remotion-2d` y `prompt-motion` son mejor opción.

## Antes de empezar

El motor es una opción gratuita (unos 400 MB) que **no se instala sola**: si falta, pide permiso en una frase y, con su «sí», `python -m universal.cli setup apply --approve film-styles` (skill `kit-onboarding`). Elige el estilo por su sentido, sea cual sea el idioma o la forma de decirlo: `python -m universal.cli catalog <palabras>` y `film-style list`. Si no está claro, propón dos o tres que encajen, descritos con palabras normales, con uno recomendado.

## Método

1. **Leer, en este orden**: `modules/opuscar/styles/<estilo>/STYLE.md` (fijo: no lo cambies), `modules/opuscar/DIRECTOR.md` (dirección y autocontrol), `modules/opuscar/TECHNIQUE.md` y `modules/opuscar/core/README.md` (construcción).
2. **Crear la carpeta**: `python -m universal.cli film-style new <estilo> out/<proyecto>/film --name "<título>" --language fr --seconds 20`. Nunca sobrescribe.
3. **Escribir `TREATMENT.md`**: tres estructuras y la elegida, **antes** de mirar la demo del estilo. Después, si hace falta una técnica: `python -m universal.cli film-style demo <estilo>` (solo para leer, al commit auditado).
4. **Escribir `index.html`** con `window.DUR`, `window.render(t)`, `window.READY`, `window.EV`, `window.TEXTS`. Cada fotograma depende solo de `t`. Sin `Date.now()` ni `Math.random()` sin semilla. Rutas absolutas: `/core/lib.js`, `/node_modules/three/...`. Dibuja según `innerWidth` e `innerHeight`.
5. **Mirar primero fotogramas**, sin renderizar el vídeo:
   ```bash
   python -m universal.cli film-style still out/<proyecto>/film 1.5 6 12 --profile final
   ```
   **Ábrelos** y compáralos con `STYLE.md`. Corrige antes de seguir.
6. **Escribir `mix.py`**: música y efectos sintetizados, desde la misma línea de tiempo.
7. **Renderizar y comprobar**:
   ```bash
   python -m universal.cli film-style render out/<proyecto>/film -o out/<proyecto>/final.mp4 --profile final
   python -m universal.cli film-style check out/<proyecto>/film
   python -m universal.cli qc --video out/<proyecto>/final.mp4 --frames out/<proyecto>/preuves
   ```
   Con `run` y el `project.json`, la película va en `out/<proyecto>/film`. `--grain 0` si el estilo trae su propio grano.
8. **Rellenar `CREDITS`** con cada recurso de terceros y su licencia. Ejemplo completo: `examples/film-style/riso-pain/`.

## Traducción de los guías al kit

Los guías vienen de otro proyecto. Donde dicen otra cosa, usa esto:

| Dicen | En este kit |
|---|---|
| `films/<name>/` | `out/<proyecto>/film/` |
| `.venv/bin/python script.py` | `python -m universal.cli film-style py script.py` |
| `node core/render/still.mjs` | `film-style still` |
| `sh core/render/mux.sh`, `film-style master` | `python -m universal.cli film-style master video.mp4 mix.wav final.mp4` |
| `build.sh` | no hace falta: `film-style render` encadena todo |
| `AGENTS.md`, `~/lemo-opuscar`, `~/lemo-my-styles` | no existen aquí: nada se instala fuera del kit |

Crear un estilo propio y guardarlo aún no está en el kit: ver `docs/ROADMAP.md`.

## Voz y música

- **Voz FR, ES, EN local y gratuita**: `python -m universal.cli voice --provider kokoro --language fr --text "..." -o voz.wav`. Es la opción «voz gratuita» (unos 550 MB): con su «sí», `setup apply --approve voice-local`. Probada en los tres idiomas. El texto escrito manda en los subtítulos; con `whisper-model` los tiempos son reales. Solo hay una voz francesa, de calidad media, y tres españolas: que el usuario la escuche.
- **Voz de pago**: ElevenLabs, con un «sí» para cada llamada.
- **Música sin descargas**: `core/audio/sfx.py` y `core/audio/pluck.py` (`modules install music`). **Instrumentos reales**: `modules install instruments-<lib> --approve-download`, de 78 a 416 Mo. El piano y la batería exigen citarlos en los créditos; `sampler.credits()` escribe el texto.

## Reglas

- **Ninguna obra, marca ni personaje ajeno** aparece en la película si el usuario no tiene el derecho. Las referencias de un `STYLE.md` enseñan una gramática, no se copian.
- Los **datos** de los estilos de pruebas (Evidence) deben ser reales y citados.
- **Mapas**: sin fronteras si la película no trata de ellas. Si hacen falta, la fuente la elige el usuario y se cita.
- Un archivo de voz o rostro real sigue pidiendo consentimiento.
- Solo el estilo Risograph se ha probado de punta a punta en este kit. Los otros 65 tienen el motor y la receta, sin película de prueba: dilo si te preguntan.
