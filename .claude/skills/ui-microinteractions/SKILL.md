---
name: ui-microinteractions
description: "Animación de interfaces y microinteracciones (inspirado en Motion Design & UI Animation): diseñar transiciones precisas para cualquier UI, definir los estados default, hover, pressed, focus, loading, success, error y disabled, y especificar duración, easing, distancia, escala, opacidad, blur y retardo de cada transición (150–350 ms), con la intención de cada movimiento y criterios de accesibilidad. Usar para botones, formularios, toggles, modales, menús, toasts, navegación, demos de producto en vídeo o handoff a desarrollo."
---

# Animación de UI y microinteracciones

Principio: la animación de UI **comunica un cambio de estado**. Corta, legible, accesible.
Prioriza **150–350 ms**. Nada que haga esperar al usuario.

## 1. Los 8 estados obligatorios

Para cada componente interactivo especifica todos (aunque alguno sea "sin cambio"):

| Estado | Qué comunica | Tratamiento de referencia |
|---|---|---|
| **default** | Disponible | — |
| **hover** | "Puedes interactuar" | +2–4 % de escala o −2 px en Y, fondo +6 % de luminosidad · 150 ms ease-out |
| **pressed** | "Te he oído" | escala 0,96–0,98 · 80–100 ms ease-out; al soltar spring de vuelta (200 ms) |
| **focus** | "Estás aquí" (teclado) | anillo de 2–3 px, offset 2 px, aparece en 120 ms · nunca solo color |
| **loading** | "Estoy trabajando" | el contenido se difumina (blur 4 px, opacidad 0) en 150 ms → spinner/esqueleto; ancho estable |
| **success** | "Hecho" | check dibujado (stroke) 250–350 ms + color de éxito; vuelta a default tras 1,5–2 s |
| **error** | "Algo falla, aquí" | shake horizontal 3 oscilaciones ±4–6 px en 300 ms + color de error + mensaje |
| **disabled** | "No disponible" | opacidad 0,4–0,5, sin hover ni pressed, cursor `not-allowed`, sin animación |

## 2. Tabla de especificación (formato de entrega)

Para cada transición entrega una fila completa:

| Transición | Disparador | Duración | Easing | Distancia | Escala | Opacidad | Blur | Retardo | Intención (1 frase) |
|---|---|---|---|---|---|---|---|---|---|
| default → hover | puntero entra | 150 ms | `cubic-bezier(.16,1,.3,1)` | Y −2 px | 1 → 1,02 | — | — | 0 | Indica que el botón es clicable sin distraer |
| hover → pressed | mousedown | 90 ms | ease-out | Y 0 | 1,02 → 0,97 | — | — | 0 | Confirmación táctil inmediata |
| pressed → loading | click válido | 200 ms | ease-in-out | — | ancho 100 % → alto (círculo) | texto 1 → 0 | texto 0 → 4 px | 0 | La acción se está procesando, sin cambiar de sitio |
| loading → success | respuesta OK | 300 ms | spring 260/22 | — | 0,8 → 1 (icono) | 0 → 1 | — | 0 | Celebra el resultado sin interrumpir |
| * → error | respuesta KO | 300 ms | ease-out | X ±6 px ×3 | — | — | — | 0 | Señala dónde está el problema |

## 3. Valores de referencia por tipo de componente

| Componente | Entrada | Salida | Notas |
|---|---|---|---|
| Botón / chip | 150 ms | 100 ms | escala ≤ 4 % |
| Toggle / checkbox | 180–220 ms | igual | el knob usa spring; el color cambia en 150 ms |
| Tooltip | 150 ms, retardo 300–500 ms | 100 ms | fade + Y 4 px |
| Dropdown / menú | 200–250 ms | 150 ms | escala 0,96 → 1 desde el origen del disparador, stagger items 20–30 ms |
| Modal / dialog | 250–300 ms | 200 ms | fondo fade 200 ms + panel Y 16 px + escala 0,98 → 1 |
| Toast / snackbar | 300 ms | 200 ms | entra desde el borde más cercano, se apila |
| Drawer / panel lateral | 300–350 ms | 250 ms | desplazamiento completo, ease-in-out |
| Cambio de página / vista | 300–400 ms | — | shared element o fade + Y 8 px; nunca > 400 ms |
| Skeleton / shimmer | ciclo 1,2–1,5 s | — | lineal (es continuo) |

Distancias: 4–16 px en UI (más distancia = más lento). Escalas: entre 0,95 y 1,05.
Blur: 2–8 px solo para transiciones de contenido. Stagger: 20–50 ms por elemento, máx. 6 elementos.

## 4. Accesibilidad (obligatorio)

- Respetar `prefers-reduced-motion: reduce`: sustituir desplazamientos/escala por fundido ≤ 150 ms o ningún movimiento.
- Nunca comunicar un estado **solo** con movimiento o color: añadir icono o texto.
- Focus siempre visible, también con animación desactivada.
- Nada que parpadee más de 3 veces por segundo.
- El feedback (pressed) debe aparecer en < 100 ms.

## 5. Implementación rápida

```css
:root {
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --ease-in: cubic-bezier(.7, 0, .84, 0);
  --ease-in-out: cubic-bezier(.65, 0, .35, 1);
  --dur-fast: 150ms; --dur-base: 250ms; --dur-slow: 350ms;
}
.btn { transition: transform var(--dur-fast) var(--ease-out), background-color var(--dur-fast) var(--ease-out); }
.btn:hover { transform: translateY(-2px) scale(1.02); }
.btn:active { transform: scale(.97); transition-duration: 90ms; }
.btn:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
.btn:disabled { opacity: .45; pointer-events: none; }
@media (prefers-reduced-motion: reduce) { * { transition-duration: 1ms !important; animation: none !important; } }
```

Para React: GSAP (`gsap-react`) o Motion (`motion/react`). En **vídeo** (demos de producto),
recrear estos estados frame a frame: ver `prompt-motion/compositions/paper-ui.html`
(botón → loading → success → tarjeta) y la skill `prompt-motion-style`.

## 6. Formato de respuesta

1. Lista de componentes y sus estados.
2. Tabla de especificación (sección 2) por componente.
3. Intención de cada movimiento en una frase.
4. Versión **sobria** (fades y escalas mínimas) y versión **audaz** (springs, morphs, blur).
5. Notas de accesibilidad y tokens CSS listos para desarrollo.
