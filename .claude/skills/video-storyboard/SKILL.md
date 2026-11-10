---
name: video-storyboard
description: "Vídeo multiescena, Reels y explainers (inspirado en HyperFrames / Motion Skills): convertir un brief en un storyboard de 4 a 8 escenas con duración, texto en pantalla, visual, movimiento principal, transición e intención; adaptar a 9:16 (Reels/TikTok/Shorts), 1:1 (feed) y 16:9 (YouTube/web); estructura hook en 2 s → valor → CTA; proponer paleta, tipografía, estilo gráfico y dirección sonora coherentes. Usar para planificar cualquier vídeo antes de producirlo."
---

# Vídeo multiescena: storyboard

## 1. Estructura obligatoria

| Bloque | Tiempo (vídeo 15 s) | Tiempo (30 s) | Función |
|---|---|---|---|
| **Hook** | 0–2 s | 0–2 s | Detener el scroll: promesa, cifra, pregunta, contradicción, imagen inesperada |
| **Valor** | 2–12 s | 2–25 s | Una idea por escena: problema → solución → prueba |
| **CTA / resolución** | 12–15 s | 25–30 s | Una sola acción, visible ≥ 2 s |

**4 escenas mínimo, 8 máximo.** Si hay más ideas, se recorta el mensaje, no el tiempo de lectura.

## 2. Plantilla de storyboard (formato de entrega)

Encabezado del proyecto:

```
Formato: 9:16 (1080×1920) · Duración: 15 s · Plataforma: Instagram Reels · 30 fps
Restricciones de marca: [logo, colores, tipografías, tono, menciones legales]
Dirección elegida: [nombre de la dirección creativa]
```

Una fila por escena:

| # | Tiempo | Texto en pantalla | Visual | Movimiento principal | Transición → | Intención |
|---|---|---|---|---|---|---|
| 1 | 0,0–2,0 s | «¿Aún haces facturas a mano?» | Fondo de marca, texto gigante | Palabras entran en stagger 40 ms, «a mano» en acento | Push hacia arriba | Hook: identificar el dolor |
| 2 | 2,0–5,0 s | «Hazlas en 10 segundos» | Captura de la app en un móvil | El móvil entra con spring, el cursor pulsa «Crear» | Zoom dentro de la pantalla | Mostrar la solución |
| … | | | | | | |
| N | 12,0–15,0 s | «Pruébala gratis» + logo | Logo + botón CTA | Logo se asienta, CTA respira | — (vuelve al frame 1 si es loop) | Acción |

Reglas de la tabla: texto ≤ 7 palabras por escena · un solo movimiento principal · la
transición describe **cómo** se conecta con la siguiente (match cut, push, morph, zoom, wipe, corte en el beat).

## 3. Adaptación de formatos

| Formato | Uso | Ajustes de composición |
|---|---|---|
| **9:16** 1080×1920 | Reels, TikTok, Shorts, Stories | Zonas seguras: 14 % arriba, 20 % abajo, 12 % derecha. Texto en el tercio central. Tipografía grande (≥ 5 % del alto). |
| **1:1** 1080×1080 | Feed, anuncios, carruseles | Composición centrada, márgenes 8 %. Reducir texto un 15 %. |
| **4:5** 1080×1350 | Feed IG/FB/LinkedIn | Como 1:1 con más aire vertical. |
| **16:9** 1920×1080 | YouTube, web, presentaciones | Composición en tercios, texto a la izquierda + visual a la derecha. Se puede ir más lento (+20 % de duración por escena). |

Indica qué cambia por formato (posición del texto, encuadre del visual, duración), no repitas el storyboard entero.

## 4. Dirección de arte y sonido (siempre proponer)

```
Paleta: fondo [hex] · texto [hex] · acento único [hex] · (secundario [hex])
Tipografía: titulares [familia + peso] · texto/labels [familia] · tamaños: título X px, subtítulo Y px (en 1080 px)
Estilo gráfico: [flat, papel, HUD oscuro, collage, 3D, UI realista, ilustración…] + textura (grano, sombras, sin degradados…)
Dirección sonora: música [género, BPM, energía] · SFX [clics, whooshes, impactos — en qué momentos] · voz en off [sí/no, tono]
  · subtítulos siempre (la mayoría se ve sin sonido)
```

Coherencia: un acento, una familia tipográfica (+ mono opcional), un tipo de transición dominante, el mismo easing.

## 5. Especificaciones técnicas

Después del storyboard aprobado, entrega las especificaciones con
`references/specs-template.md`: keyframes por escena, easing, transiciones, textos finales,
lista de assets y exportación.

## 6. Versión sobria y versión audaz

Entrega el storyboard en su versión principal y añade una tabla corta de diferencias
(ver `motion-director`): ritmo, transiciones, tipografía, color y sonido de cada versión.

## 7. Producción

Con el storyboard aprobado → skill `motion-kit` (elige motor y produce). Correspondencias útiles:
Remotion `Promo-*` / `Kinetic-*` (template), HyperFrames `general-video`, `product-launch-video`,
`faceless-explainer`, `music-to-video`, o el estilo `prompt-motion-style`.
