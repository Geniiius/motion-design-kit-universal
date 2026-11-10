---
name: remotion-motion-graphics
description: "Crear y editar vídeos de motion graphics profesionales con Remotion (vídeo hecho con React). Usar CADA VEZ que se quiera crear o editar un vídeo, animar algo, hacer una intro/outro/animación de logo, un Reel/Short/promo/vídeo de lanzamiento, añadir animaciones de texto o subtítulos a un clip, combinar imágenes y B-roll, o se mencione Remotion, motion graphics, render de vídeo o «haz que este vídeo se vea mejor / menos genérico». También al editar un proyecto Remotion existente o cuando el vídeo se ve básico, genérico o amateur: esta skill contiene las correcciones exactas. Leerla SIEMPRE antes de escribir código Remotion."
---

# Motion graphics con Remotion

Remotion renderiza componentes React fotograma a fotograma para crear vídeo. El cuello de
botella no es la calidad del código, sino **el oficio de motion design**. Sin método se obtiene
easing lineal, fundidos de opacidad solos, entradas simultáneas, colores planos y sin textura:
el look de «vídeo genérico hecho por IA». Esta skill existe para evitarlo.

## Reglas innegociables (en CADA composición)

1. **NUNCA interpolación lineal.** Cada `interpolate()` lleva una curva de easing; cada
   entrada prefiere `spring()`. Siempre `extrapolateLeft/Right: "clamp"`.
2. **Las entradas animan 2–3 propiedades a la vez** (opacidad + translateY + escala).
   Un fundido solo está prohibido.
3. **Stagger en todo.** Listas, palabras, rayos, tarjetas: desfases de 3–6 frames.
   Nada entra a la vez.
4. **Las salidas existen y son más rápidas que las entradas** (~10 frames frente a ~20).
5. **Cinco capas en cada escena**, de abajo arriba: fondo degradado animado → assets →
   gráficos/tipografía → etalonaje → grano + viñeta. Nunca un fondo plano.
6. **Toda imagen fija lleva Ken Burns** (escala lenta 1→1,08 + paneo). Todo vídeo usa
   `<OffthreadVideo>`, nunca `<Video>`.
7. **Los elementos en reposo respiran**: todo lo que esté en pantalla > 2 s lleva un
   micromovimiento sinusoidal.
8. **Todo el timing se deriva de `fps`** con `useVideoConfig()`. Nada de números de frame mágicos.
9. **Un único objeto de tema** al principio del proyecto (colores, easings, springs,
   tipografías). Nunca un color hexadecimal o un easing escrito dentro de un componente.
10. **Renderizar, extraer fotogramas, MIRARLOS, corregir, volver a renderizar.** Nunca entregar
    un render sin verificar. Este bucle es obligatorio (ver Verificación).

## Flujo de trabajo

### Paso 1 — Alcance
Determinar: duración, fps (30 por defecto; 60 solo con movimiento muy rápido), dimensiones
(1080×1920 Reels/Shorts, 1920×1080 horizontal), assets disponibles (imágenes, vídeos, audio,
logos) y si es una composición nueva o la edición de un proyecto existente. Si se edita un
proyecto: leer `src/` entero primero, localizar el tema (o crearlo) y corregir las infracciones
de las reglas antes de añadir nada.

### Paso 2 — Preparación
En el kit: usar `template/` (ya instalado). Proyecto nuevo desde cero:
```bash
npm install remotion @remotion/cli react react-dom
# opcional: @remotion/transitions @remotion/motion-blur @remotion/google-fonts
```
Copiar `assets/theme.ts` de esta skill a `src/theme.ts` y ajustar la paleta a la marca.
Estructura: `src/index.ts` (registerRoot) → `src/Root.tsx` (Composition, duración/fps/tamaño)
→ `src/scenes/*.tsx` → `src/components/*.tsx`. Los assets van en `public/` y se cargan con
`staticFile()`.

### Paso 3 — Construcción
Leer `references/motion-patterns.md` para los componentes reutilizables (fondo animado,
etalonaje, grano, viñeta, Ken Burns, revelado palabra a palabra, stagger, contador, destello,
transiciones, parallax). Componer las escenas con esos patrones. Para ritmo, tipografía,
paletas y diseño sonoro, leer `references/design-rules.md`.

Ritmo de escena: IMPACTO → pausa (15–20 frames quietos) → construcción → IMPACTO. Algo debe
moverse en los primeros 15 frames. Nunca más de 90 frames sin un elemento visual nuevo.

### Paso 4 — Render
```bash
npx remotion render src/index.ts <IdComposicion> out/video.mp4 --codec h264 --crf 17
```
Remotion necesita Chromium. Si la descarga automática falla, ejecutar
`npx remotion browser ensure` o indicar uno con `--browser-executable=<ruta>`.

### Paso 5 — VERIFICAR (obligatorio, nunca saltarlo)
Extraer fotogramas en los momentos clave y revisar cada uno visualmente:
```bash
npx remotion still <IdComposicion> out/check_45.png --frame=45 --scale=0.4
```
Con el MP4 terminado (verifica también la codificación):
```bash
ffmpeg -v error -ss 1.5 -i out/video.mp4 -frames:v 1 check_1.png
```
Buscar y corregir, por orden de frecuencia:
- **Errores de espaciado**: `gap`/`margin` en `em` se calcula con el tamaño de letra del PADRE
  (a menudo 16 px), no del texto: usar px en contenedores flex con tipografía grande.
- Texto que desborda o toca los bordes (en 9:16, contenido crítico en el 75 % central vertical:
  la interfaz de la plataforma tapa arriba y abajo).
- Elementos visibles antes de su entrada o después de su salida (falta `clamp`).
- Problemas de color/contraste: color protagonista en más de un elemento por fotograma, texto
  apagado ilegible sobre el etalonaje.
- Orden de capas incorrecto (grano/viñeta siempre arriba, etalonaje encima del contenido).
Corregir → renderizar → extraer → revisar. Entregar solo tras una pasada limpia y la checklist
final de `references/design-rules.md`.

### Editar un vídeo existente del usuario
Para mejorar un MP4 (subtítulos, etalonaje, intro/outro): ponerlo en `public/`, usarlo como
capa de asset con `<OffthreadVideo src={staticFile("clip.mp4")} />`, fijar la duración de la
composición según el clip (`ffprobe`) y apilar gráficos/etalonaje/grano encima. Para subtítulos
sincronizados con la voz, ver la sección de subtítulos de `references/motion-patterns.md`
(y la skill `speech-to-text` de ElevenLabs para transcribir).

## Archivos de referencia
- `references/motion-patterns.md` — biblioteca de componentes para copiar y pegar.
- `references/design-rules.md` — paletas, tipografía, arquitectura de escenas, sonido, checklist.
- `assets/theme.ts` — plantilla de tema para copiar en cada proyecto.

## Errores frecuentes que hay que evitar
- **Emojis como iconos.** Se renderizan con los colores de la plataforma, rompen la paleta y
  pueden desaparecer sobre fondos del mismo color. Dibujar los iconos en CSS/SVG con los
  colores del tema.
- **No tener efectos de sonido no es excusa para entregar en silencio.** Generarlos con la
  skill `sound-effects` (ElevenLabs) o `motion-sound-effects`.
- Un único componente gigante en vez de piezas reutilizables con tema.
- `durationInFrames` distinto entre la Composition y el contenido (tiempo muerto).
- Olvidar sobrescribir los renders y revisar un archivo antiguo.
- Tipografías: nunca depender de las fuentes del sistema para los titulares; cargar una con
  `@remotion/google-fonts` o `@font-face` + `staticFile`.
- «Describir» el resultado al usuario en lugar de renderizarlo y verificarlo.
