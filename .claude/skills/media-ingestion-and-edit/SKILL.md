---
name: media-ingestion-and-edit
description: "Montar medios existentes en local con FFmpeg: inventario real, planche de contacto, plan de montaje con cortes y fundidos, fotos con encuadre vivo, clips verticales en formato horizontal, logo, voz sobre música atenuada, subtítulos, -14 LUFS. Usar para montar rushes, clips, fotos y audio sin generar nada."
---

# Ingesta y montaje

**Los originales no se tocan.** No uses un motor de generación para un corte. Para efectos alrededor de una persona (texto detrás de la cabeza, seguimiento de la cara): skill `video-effects`. Para tratar **un** vídeo entregado (silencios, extractos, vertical, subtítulos, traducciones, capítulos): skill `video-workflows`. Para obtener el minuto exacto de cada palabra sin conexión: `python -m universal.cli transcribe clip.mp4 -o palabras.json`.

```bash
python -m universal.cli inventory clip.mp4 foto.jpg
python -m universal.cli contact-sheet clip1.mp4 clip2.mp4 -o out/reperage.jpg
python -m universal.cli route --brief "Monta estos clips" -i clip1.mp4 -i clip2.mp4 -i logo.png::logo -i voz.wav::voice -i musica.mp3::music --name proyecto -o out/proyecto/project.json
python -m universal.cli run out/proyecto/project.json --profile review
```
Sin `timeline.edl` monta **los medios enteros, en orden**: cortar es una decisión, nunca un valor por defecto. Solo una duración pedida («en 30 segundos») acorta los clips, a partes iguales y conservando el principio de cada uno, y el resultado lo dice en `montage` con «à vérifier»: mira qué pasajes han quedado. Con `timeline.edl` decides tú: `{"src": "...", "in": 1.2, "seconds": 3, "transition": "fade", "fade_s": 0.4}`.
Un solo vídeo, sin formato pedido, sale con su propia forma.

- Clip vertical en formato horizontal: conserva la imagen entera sobre un fondo desenfocado.
- Respeta la cronología si se pide. **Nunca cortes una frase por la mitad**: con voz real, transcribe primero en local (`transcribe`, gratis y sin conexión; la descarga de 345 Mo se pregunta) y corta en finales de palabra.
- Rotación y cadencia variable: `inventory` las avisa.

Corte automático de silencios: skill `video-workflows`. Quitar tomas repetidas y errores: Herk Edit Kit, opcional. Recetas sueltas: skill `ffmpeg-video`.
