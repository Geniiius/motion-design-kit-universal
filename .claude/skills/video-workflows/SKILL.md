---
name: video-workflows
description: "Tratar UN vídeo que el usuario entrega, sin rehacerlo: quitar silencios, sacar extractos cortos, reencuadrar para otro formato (vertical, cuadrado), subtítulos incrustados o en archivo, traducir los subtítulos y escribir capítulos. Todo local con FFmpeg y transcripción sin conexión. Usar con podcasts, entrevistas, tutoriales, cara a cámara o un vídeo largo que hay que adaptar a YouTube, TikTok, Instagram o Shorts."
---

# Tratamientos de un vídeo entregado

El vídeo se conserva **entero**: solo cambia lo que la persona pide. Sin formato pedido, sale con su propia forma (un vídeo vertical sigue vertical). **Nada se entrega por adivinación**: cuando hace falta leer o elegir, el kit se para y te lo pide a ti.

Con el usuario, palabras normales: «Le quito los silencios y le pongo subtítulos», nunca nombres de tratamientos ni comandos.

## Qué sabe hacer

| La persona dice | Tratamiento | Qué hace | Necesita |
|---|---|---|---|
| «quita los silencios», «los tiempos muertos» | `silence-cut` | Corta el interior de cada silencio y deja un respiro a cada lado | Solo FFmpeg |
| «saca extractos», «los mejores momentos» | `clips` | Un archivo por momento, cortado en finales de palabra | Transcripción local para elegir |
| «hazlo vertical», «para TikTok / Reels / Shorts» | `reframe` | Sigue la cara, corta al centro o conserva todo sobre fondo desenfocado | Seguir la cara: módulo de efectos |
| «ponle subtítulos», «tradúcelo al inglés» | `captions` | Subtítulos incrustados o en archivo, en el idioma hablado y en traducciones | Transcripción local |
| «ponle capítulos» | `chapters` | El texto de capítulos que lee una plataforma. El vídeo no cambia | Transcripción local para leer |

Lista viva: `python -m universal.cli workflows`. El orden lo fija el kit (silencios, extractos, reencuadre, subtítulos, capítulos) y solo hay una codificación final.

## Enrutar

```bash
python -m universal.cli route --brief "<sus palabras>" -i video.mp4 --name <proyecto> -o out/<proyecto>/project.json
python -m universal.cli run out/<proyecto>/project.json --profile draft
```
- Si la persona lo dice de otra manera («corta cuando no digo nada»), el enrutador no lo reconoce: díselo tú con `--workflow silence-cut` (repetible).
- Un logo, una música o una voz entregados con el vídeo (`-i logo.png::logo`) se ponen en la codificación final.
- **Varios clips** no son un tratamiento sino un montaje (skill `media-ingestion-and-edit`): monta primero y trata después la película montada.
- Nombrar una plataforma fija la forma y añade el reencuadre. «Instagram» a secas es vertical; «feed» es 4:5.

## Lo que `run` responde

| Estado | Qué significa | Qué haces |
|---|---|---|
| `delivered` | Archivos escritos y controlados | Mira los fotogramas, luego `quality-reviewer` |
| `needs-input` | El kit ha preparado un archivo y espera tu lectura o tu elección | Haz lo que dice el mensaje y relanza. No es un fallo |
| `unchanged` | Ningún tratamiento ha cambiado nada (por ejemplo, no había silencios) | Díselo a la persona: su vídeo ya estaba bien. No hay archivo nuevo |
| `failed` | El control de calidad bloquea | Lee `qc.json`, corrige, relanza |

## Tus decisiones, en `props.workflow` del manifiesto

**Subtítulos** (`captions`). La transcripción se equivoca con nombres propios y palabras parecidas, así que nunca se incrusta sin leer:
1. El primer `run` escribe `<proyecto>.<idioma>.srt` y se para.
2. Lee el archivo entero y corrige **solo el texto**, sin tocar números ni horarios. Si dudas de un nombre propio, pregunta a la persona.
3. Pon `"captions": {"reviewed": true}` y relanza. Si la transcripción se rehace, el kit borra ese «leído» él solo.
- Traducciones: `"languages": ["en", "es"]` (el enrutador lo rellena si la petición nombra idiomas). Las escribes tú en `<proyecto>.<idioma>.srt`, **con los mismos números y horarios** que el archivo corregido. Ningún servicio externo. Una traducción que se lee demasiado rápido se acorta: el kit lo exige.
- `"mode": "file"` entrega los `.srt` sin incrustar nada. `"spoken": "es"` fuerza el idioma hablado si la detección falla.
- Con varios idiomas sale un vídeo por idioma (`-en`, `-es`).

**Extractos** (`clips`). El primer `run` escribe `<proyecto>.transcription.txt` con los tiempos. Léelo y elige momentos que **se sostienen solos**: una idea completa, un arranque que engancha, nada que dependa de lo anterior. Escribe `"clips": [{"in": 12.4, "out": 41.0, "title": "..."}]` (3 s como mínimo) y relanza. Si la persona da los minutos, úsalos tal cual. Sin habla reconocida, pídele los momentos.

**Reencuadre** (`reframe`). `"mode"`: `auto` (por defecto: sigue la cara si la encuentra casi siempre, y si no conserva todo sobre fondo desenfocado), `face`, `center`, `blur`. Seguir una cara es un tratamiento local del rostro de una persona: di que se hace en su ordenador. Si el encuadre se agranda mucho, el kit avisa de que pierde nitidez: propón el fondo desenfocado.

**Silencios** (`silence-cut`). Ajustes si corta de más o de menos: `"threshold_db"` (más negativo corta menos), `"min_silence_s"` (0,6 por defecto), `"padding_s"` (0,12). Los valores por defecto viven en `kit.config.json`.

**Capítulos** (`chapters`). El primer `run` escribe la transcripción. Marca dónde cambia el tema: `"chapters": [{"t": 0, "title": "Introducción"}, ...]`, al menos 3, el primero en 0 y 10 s entre dos. Sale `<proyecto>.chapitres.txt`, listo para pegar en la descripción.

## Antes de instalar o descargar

La transcripción local (unos 345 Mo) y el seguimiento de la cara (unos 500 Mo) son gratuitos, pero **se preguntan**: «Para los subtítulos necesito descargar una herramienta gratuita de 345 Mo que funciona sin conexión. ¿La descargo?». Sin el seguimiento de la cara, el reencuadre automático conserva la imagen entera sobre fondo desenfocado y lo dice.

## Comprobar

- Mira fotogramas en varios momentos: subtítulos legibles, dentro del cuadro y por encima del cuarto inferior en vertical, donde la plataforma pone sus botones.
- Escucha dos o tres cortes de silencios: ninguna palabra comida.
- En un extracto, la primera y la última palabra enteras.
- Di la ruta exacta de cada archivo final, y las notas del resultado en palabras normales («He quitado 7 segundos de silencios en 4 cortes»).

## Límites, dichos tal cual

- El kit no decide solo qué momentos son «los mejores»: eso lo lees tú. No quita muletillas («eh», «o sea») ni repeticiones: solo silencios.
- No separa a varios hablantes ni sigue a dos caras a la vez: con dos personas, propón el fondo desenfocado o el corte al centro.
- El seguimiento de la cara se ha probado con trayectorias simuladas, **no con una persona real filmada**: mira el resultado entero antes de entregarlo.
- Transcribir tarda: en el portátil de pruebas, un tercio de la duración del vídeo (una hora, unos 18 minutos). Avisa antes de empezar con un vídeo largo.
