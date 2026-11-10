---
name: motion-kit
description: "Referencia de los motores de creación del kit (Remotion, HyperFrames, Prompt Motion): cuál usar, dónde están y qué skills cargar para escribir una composición, y el bucle render → verificación → exportación. Usar después de universal-motion-director, cuando el vídeo se crea desde cero. Para tratar un vídeo entregado: video-workflows; para montar: media-ingestion-and-edit."
---

# Motion Design Kit — enrutador

El kit tiene varios motores de vídeo y ElevenLabs como opción de audio de pago. Este archivo
decide **qué usar** y luego delega. Raíz del kit: la carpeta que contiene `CLAUDE.md` (ver `LEEME.md`). El audio es local por defecto; ElevenLabs solo con un «sí» para cada llamada.

## 0. Enrutar y dirección creativa

Si aún no hay `project.json`, empieza por **`universal-motion-director`**: lee los archivos y elige el camino. Este archivo detalla el camino Remotion.


Para cualquier brief nuevo, aplicar primero la skill **`motion-director`**: preguntas que
falten → **3 direcciones creativas** → elección del usuario → storyboard (`video-storyboard`)
→ especificaciones (`motion-fundamentals`, `ui-microinteractions`), versión sobria + audaz.
Solo pasar a la producción tras la validación (salvo que el usuario diga «ve directo»).

## 1. Brief mínimo

Plataforma · objetivo · duración · assets (logo, imágenes, vídeos, música, voz, URL) · tono /
paleta. Si falta algo no bloqueante, elegir un valor por defecto y decirlo.
Formatos y duraciones: `references/formats.md`. Estructuras narrativas: `references/storytelling.md`.

## 2. Elegir el motor

| Necesidad | Motor | Dónde | Skills |
|---|---|---|---|
| Promo, Reel de texto, logo, datos, varios formatos desde un mismo código, props editables | **Remotion** (React) | `template/` | `remotion-motion-graphics`, `remotion-best-practices` (+ `remotion-captions`, `remotion-render`…) |
| Vídeo HTML/CSS/GSAP, lanzamiento de producto, explainer, presentación, web → vídeo | **HyperFrames** (HeyGen) | `hyperframes-starter/` o `npx hyperframes init` | `hyperframes`, `general-video`, `product-launch-video`, `motion-graphics`, `faceless-explainer`, `music-to-video`… |
| Estilo **prompt-motion.com**: UI que se transforma con un cursor, showreel, HUD negro/naranja, bucle al BPM | **Prompt Motion** (HTML `seek(t)`) | `prompt-motion/` | `prompt-motion-style` (+ `claude-motion-design` para proyectos largos) |
| **Tratar un vídeo entregado** (pódcast, entrevista, tutorial, cara a cámara): quitar silencios, extractos, vertical, subtítulos, traducciones, capítulos | **Tratamientos del kit** (FFmpeg, local) | raíz del kit | `video-workflows` |
| Montaje de cara a cámara con tomas repetidas y errores que quitar, B-roll | **Herk Edit Kit** (opcional) | `workspaces/herk-edit-kit/` → abrir Claude **dentro de esa carpeta** | `make-a-video`, `short-form-edit`, `cut-mistakes`, `video-storytelling` |
| Film de lanzamiento «de agencia», remake de un vídeo de referencia | **HTML + Playwright + ffmpeg** | skill global | `claude-motion-design` |
| Explainer con voz en off sincronizada | Remotion o HyperFrames | — | `explainer-default` / `explainer-engaging` / `explainer-high-energy`, `motion-broll` |

Principios transversales: `motion-fundamentals`, `motion-design` (LottieFiles), `gsap-*` al escribir GSAP.

**Por defecto**: Remotion para diseño puro y varios formatos; HyperFrames si se quiere
HTML/GSAP o una de sus skills encaja exactamente; Prompt Motion para el look «Dribbble / showreel».

## 3. Audio y voz con ElevenLabs

Audio local gratuito: `python -m universal.cli voice`. **ElevenLabs** es de pago: cada llamada necesita un «sí» (conector de Claude o API key, ver `LEEME.md`):

| Necesidad | Skill / herramienta |
|---|---|
| Voz en off | `text-to-speech` (o la herramienta de voz del conector ElevenLabs) |
| Música de fondo | `music` (requiere API key o el conector ElevenLabs completo) |
| Efectos de sonido (whoosh, clic, impacto) | `sound-effects` |
| Transcripción → subtítulos | `speech-to-text` |
| Configurar / comprobar la API key | `setup-api-key` |

Flujo: escribir el guion con los tiempos del storyboard → generar la voz → medir su duración
(`ffprobe`) y ajustar las escenas a ella → generar música (BPM del storyboard) y efectos →
mezclar con `template/scripts/ffmpeg/add-audio.ps1` (ducking automático) o con `<Audio>` en Remotion.
Guardar los archivos en `template/public/audio/` (`voz/`, `musica/`, `sfx/`).
Sin conector ni API key: voz local si existe en el idioma, si no, avisar y renderizar sin sonido.

## 4. Bibliotecas de animación en `template/`

| Librería | Uso | Componente / helper |
|---|---|---|
| Remotion `spring`/`interpolate` | base de todo | `KineticText`, `CTA`, `Background`, `Grain` |
| **GSAP** | timelines complejas, letra a letra, easings ricos | `src/lib/gsap.ts` → `useGsapTimeline()` (timeline en pausa + `seek(frame/fps)`), ejemplo `GsapTitle` |
| **Motion** (motion.dev) | springs físicos, `interpolate` con varios keyframes, `backOut`/`anticipate` | `MotionStats` — solo funciones puras, nunca `<motion.div>` (tiempo real ≠ render por fotograma) |
| **lottie-web** con `@remotion/lottie` | iconos/ilustraciones animadas de After Effects o LottieFiles | `LottieClip src="lottie/x.json"` |

Regla de oro: **toda animación depende del fotograma actual**. Nada de `setTimeout`,
`transition`/`animation` CSS ni `requestAnimationFrame`.

## 5. Flujo Remotion (template)

1. `cd template` · assets en `public/` (`images/`, `audio/`, `lottie/`, `footage/`, `captures/`).
2. Duplicar una composición de `src/compositions/` o cambiar sus `defaultProps`
   (esquema zod → editable en el Studio). Paleta con la prop `palette` (`src/theme.ts`).
3. Vista previa: `npm run studio`.
4. **Verificar antes de entregar**: `npx remotion still <Id> out/check/x.png --frame=N --scale=0.4`
   en 3–5 fotogramas clave (hook, mitad, CTA) y **mirar las imágenes**. Corregir. Repetir.
5. Renderizar: `npx remotion render <Id> out/<nombre>.mp4` o `.\scripts\render-all.ps1 -Filtro Promo`.
6. Control final: `.\scripts\ffmpeg\extract-frames.ps1 out\<nombre>.mp4` → mirar las imágenes.
7. Exportar: `.\scripts\ffmpeg\social-export.ps1 out\<nombre>.mp4 -Plataforma instagram` (normaliza a -14 LUFS).
8. Control de calidad: `.\scripts\control-calidad.ps1 out\<nombre>-instagram.mp4 -Proyecto "<nombre>" -Plataforma instagram`
   → corregir lo que salga en MEJORAR, luego retrospectiva y perfil (skill `motion-memoria`, parte B).

## 6. Assets

- **Web / app que promocionar** → skill `playwright-capture` o `npx hyperframes capture <url>`.
- **Grabaciones** → `scripts/ffmpeg/prepare-footage.ps1` (recorte al formato + 30 fps).
- **Audio** → sección 3 (ElevenLabs).
- **Subtítulos** → `remotion-captions` (Remotion) o `embedded-captions` (HyperFrames).
- Comandos ffmpeg avanzados → skill `ffmpeg-video`.

## 7. Checklist de calidad (no entregar si falla un punto)

- Hook legible en los **2 primeros segundos**, texto ≥ 5 % de la altura en móvil.
- Texto fuera de las zonas tapadas (Reels/TikTok: 14 % arriba, 20 % abajo, 12 % derecha).
- Ninguna animación lineal, entradas en stagger, salidas más rápidas que las entradas.
- Nunca fondo plano: degradado animado + grano/viñeta.
- Final con CTA claro (≥ 2 s en pantalla) en todo vídeo promocional.
- Audio: voz inteligible, música por debajo de la voz, subtítulos (la mayoría lo ve sin sonido).
- Exportación H.264 / yuv420p / AAC / faststart (el script lo hace).
