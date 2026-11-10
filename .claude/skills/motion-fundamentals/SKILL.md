---
name: motion-fundamentals
description: "Fundamentos de motion design (inspirado en LottieFiles Motion Design Skill): definir objetivo, mensaje, emoción, duración, plataforma y jerarquía antes de animar; dirección de movimiento (timing, ritmo, easing, anticipación, overlap, follow-through, coreografía); narrativa visual entrada → énfasis → transición → salida. Usar en cualquier proyecto de animación o vídeo para que cada movimiento mejore la comprensión y no solo decore."
---

# Fundamentos de motion design

Complementa la skill `motion-design` (LottieFiles, principios Disney aplicados) con un marco
de decisión. Regla madre: **cada animación debe mejorar la comprensión, no solo decorar.**

## 1. Antes de animar: la ficha de intención

Rellénala (aunque sea mentalmente) antes de proponer cualquier movimiento:

| Campo | Pregunta | Ejemplo |
|---|---|---|
| Objetivo | ¿Qué debe pasar después de verlo? | Que descarguen la app |
| Mensaje clave | ¿Qué frase debe recordar? (≤ 8 palabras) | «Tus facturas, hechas en 10 s» |
| Emoción | ¿Qué debe sentir? | Alivio, control |
| Duración | ¿Cuánto tiempo real de atención hay? | 15 s |
| Plataforma | ¿Dónde y cómo se ve? (sonido, tamaño, scroll) | Reels, sin sonido, móvil |
| Jerarquía visual | ¿Qué es 1º, 2º y 3º en importancia? | 1. beneficio · 2. producto · 3. logo |

## 2. Dirección de movimiento

### Timing (duraciones de referencia a 30 fps)
| Tipo de movimiento | Duración | Frames |
|---|---|---|
| Microinteracción UI | 150–350 ms | 5–10 |
| Entrada de texto / elemento | 400–700 ms | 12–21 |
| Salida | 60–70 % de la entrada | 8–14 |
| Transición entre escenas | 300–600 ms | 9–18 |
| Movimiento de cámara / reveal | 800–1500 ms | 24–45 |
| Tiempo de lectura de un texto | 0,3 s por palabra + 1 s | — |

Los elementos grandes y lejanos se mueven más despacio; los pequeños y cercanos, más rápido.

### Ritmo
- Alterna **tensión y respiro**: tras 2–3 cambios rápidos, deja un plano que respire (≥ 1 s).
- Si hay música, cala los cambios en los tiempos (120 BPM = 0,5 s por tiempo).
- Varía las duraciones: un ritmo totalmente regular se vuelve monótono.

### Easing (biblioteca coherente — usar siempre las mismas)
| Uso | Curva | cubic-bezier |
|---|---|---|
| Entradas (llega y se asienta) | ease-out expo | `(0.16, 1, 0.3, 1)` |
| Salidas (acelera y se va) | ease-in | `(0.7, 0, 0.84, 0)` |
| Desplazamientos en pantalla | ease-in-out | `(0.65, 0, 0.35, 1)` |
| Objetos físicos / UI "viva" | spring | stiffness 180–260, damping 20–26 |
| Énfasis con carácter | back-out (overshoot leve) | `(0.34, 1.56, 0.64, 1)` |

**Lineal solo** para: rotaciones continuas, barras de progreso reales, scroll de créditos.

### Principios clave
- **Anticipación**: un pequeño movimiento contrario antes del principal (−3 a −8 % de la amplitud, 80–150 ms). Prepara el ojo.
- **Overlap / desfase**: las partes de un objeto no se detienen a la vez (texto 50–100 ms después de su contenedor).
- **Follow-through**: tras parar, un ligero rebote o asentamiento (1 oscilación máximo).
- **Stagger / coreografía**: elementos de una lista entran con 30–80 ms de desfase, en el orden de lectura.
- **Combinación de propiedades**: una entrada mueve 2–3 propiedades a la vez (opacidad + desplazamiento + escala/blur). Un fundido solo es pobre.
- **Arcos**: los desplazamientos largos siguen curvas, no líneas rectas.
- **Continuidad**: el elemento que sale debería "entregar" el foco al que entra (match cut, morph, misma dirección).

## 3. Narrativa visual en 4 tiempos

Cada escena (y el vídeo completo) sigue:

1. **Entrada** — aparece lo necesario, en orden de jerarquía. Rápida y clara.
2. **Énfasis** — el momento clave: la palabra resaltada, el número que sube, el clic. Un solo énfasis por escena.
3. **Transición** — conecta con la siguiente idea; la dirección del movimiento tiene sentido (adelante = derecha/arriba).
4. **Salida** — más rápida que la entrada; nunca dejar elementos "muertos" en pantalla.

## 4. Checklist del movimiento (para cada animación)

- ¿Qué ayuda a entender? → si no hay respuesta, se elimina.
- ¿Dónde está el ojo antes y después?
- ¿El easing es el de la biblioteca?
- ¿La duración está en el rango de su tipo?
- ¿Hay como mucho **un** foco de atención en movimiento a la vez?
- ¿Respeta `prefers-reduced-motion` (en UI) o hay una alternativa sobria?
