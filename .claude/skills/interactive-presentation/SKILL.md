---
name: interactive-presentation
description: "Presentaciones HTML de verdad, navegables con clic, teclado y táctil: menú, capítulos, demos antes/después, puntos interactivos, adaptadas al móvil, y aparte una película lineal. Usar para catálogos de servicios, decks interactivos o presentaciones que el visitante recorre."
---

# Presentación interactiva

**Dos salidas distintas.** Un MP4 no contiene botones: nunca presentes un clic simulado como interactividad.

```bash
python -m universal.cli present -c examples/universal/services.json -o out/services.html   # interactivo
python -m universal.cli film out/services.html -o out/services-film.mp4                    # película lineal, sin clics
node tests/deck.spec.mjs out/services.html out/pruebas                                     # 13 pruebas con Chromium real
```

## Contenido por servicio (`services[]`)
`title`, `summary`, `description`, `benefits[]`, `price`, `url`, y demos: `before_after {before, after}`, `steps [{title, text}]`, `hotspots [{x, y, label, note}]`.
`language`: `es`, `fr` o `en`.

**Precios y beneficios verificados**: sin `price` muestra «a consultar». No inventes tarifas ni cifras.

## Ya incluido
Sin dependencias ni red, foco visible, flechas y Esc, enlace directo `#service-2`, móvil sin desplazamiento lateral, objetivos de 44 px, `prefers-reduced-motion`, texto escapado.

HyperFrames `slideshow` es una alternativa si se quieren notas de presentador. Reveal.js no se adoptó: ver `docs/THIRD-PARTY.md`.
