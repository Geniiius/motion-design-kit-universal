---
name: ffmpeg-video
description: "Recetas FFmpeg para la posproducción de vídeo motion design: exportación para redes sociales (Instagram, TikTok, YouTube, LinkedIn), recorte a 9:16/4:5/1:1/16:9, añadir música/voz con ducking, fundidos, GIF, extracción de fotogramas para verificar, cortes, concatenación, velocidad, compresión, subtítulos incrustados, volumen. Usar cuando haya que convertir, comprimir, cortar, unir, mezclar audio o verificar un vídeo renderizado."
---

# FFmpeg para motion design

Scripts listos en `template/scripts/ffmpeg/` (PowerShell) — preferirlos a los comandos a mano:

| Script | Función |
|---|---|
| `social-export.ps1 <video> -Plataforma instagram\|tiktok\|youtube\|linkedin\|x\|web` | Recodifica con las especificaciones (H.264 High, yuv420p, AAC 48 k, faststart, volumen normalizado a -14 LUFS, pista muda si no hay audio) |
| `extract-frames.ps1 <video> -Cantidad 8` | Fotogramas repartidos por el vídeo → `frames/` para **verificación visual** |
| `add-audio.ps1 <video> -Musica m.mp3 [-Voz v.mp3]` | Música en bucle + fundidos; con voz: ducking automático |
| `prepare-footage.ps1 <clip> -Formato reel [-Inicio 3 -Duracion 6]` | Recorta al formato (relleno), 30 fps constantes → `public/footage/` |
| `to-gif.ps1 <video> -Ancho 480 -Fps 15` | GIF con paleta optimizada |

Comprobar siempre un resultado:
`ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate -of compact <archivo>`.

## Recetas útiles

```bash
# Cortar sin recodificar (rápido, corta en keyframe)
ffmpeg -ss 00:00:05 -to 00:00:12 -i in.mp4 -c copy out.mp4

# Cortar con precisión (recodifica)
ffmpeg -ss 5 -i in.mp4 -t 7 -c:v libx264 -crf 18 -c:a aac out.mp4

# Unir clips del mismo formato
#   lista.txt :  file 'a.mp4'  /  file 'b.mp4'
ffmpeg -f concat -safe 0 -i lista.txt -c copy out.mp4

# 16:9 -> 9:16 con fondo desenfocado (en lugar de recortar)
ffmpeg -i in.mp4 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -c:a copy out.mp4

# Acelerar x2 (vídeo + audio)
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" out.mp4

# Cámara lenta fluida (interpolación de movimiento)
ffmpeg -i in.mp4 -vf "minterpolate=fps=60,setpts=2*PTS" out.mp4

# Fundido a negro entrada/salida (vídeo de 10 s)
ffmpeg -i in.mp4 -vf "fade=t=in:d=0.5,fade=t=out:st=9.5:d=0.5" -af "afade=t=in:d=0.5,afade=t=out:st=9.5:d=0.5" out.mp4

# Incrustar subtítulos .srt (estilo Reel)
ffmpeg -i in.mp4 -vf "subtitles=subs.srt:force_style='FontName=Inter,FontSize=14,Bold=1,Outline=2,Alignment=2,MarginV=120'" out.mp4

# Normalizar el volumen (redes sociales ≈ -14 LUFS)
ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy out.mp4

# Extraer el audio / quitar el audio
ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 audio.mp3
ffmpeg -i in.mp4 -an -c:v copy mudo.mp4

# Duración de una voz en off generada con ElevenLabs (para ajustar las escenas)
ffprobe -v error -show_entries format=duration -of csv=p=0 voz.mp3

# Vídeo → secuencia PNG / PNG -> vídeo
ffmpeg -i in.mp4 frames/%04d.png
ffmpeg -framerate 30 -i frames/%04d.png -c:v libx264 -pix_fmt yuv420p out.mp4

# WebM transparente -> MOV ProRes 4444 con alfa para Premiere/After Effects
ffmpeg -i in.webm -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le out.mov

# Hoja de contactos (todo el vídeo en una imagen)
ffmpeg -i in.mp4 -vf "fps=1,scale=270:-2,tile=6x3" -frames:v 1 contactos.png
```

## Errores frecuentes
- `pix_fmt` debe ser `yuv420p` (si no, pantalla negra en iPhone / Instagram).
- `-ss` **antes** de `-i` para cortar rápido, después para precisión al fotograma.
- Las capturas de Playwright son `.webm` con fotogramas variables → pasar por `prepare-footage.ps1` antes de Remotion.
- En PowerShell, no llamar nunca a una variable `$Input` (variable automática).
