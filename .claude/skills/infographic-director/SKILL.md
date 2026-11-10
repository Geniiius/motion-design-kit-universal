---
name: infographic-director
description: "Vídeos explicativos e infografías a partir de un texto, un archivo o un conjunto de datos: objetivos, guion, piezas animadas, voz, subtítulos y exportación, sin inventar ninguna cifra. Usar para explainers, vídeos científicos o pedagógicos, gráficos, cronologías y diagramas."
---

# Director de infografías

**Nunca inventes una cifra.** Cada número en pantalla sale de un archivo citado. Muestra fuente, unidad, fecha, hipótesis e incertidumbre. Sin fuente, pídela o di que es ilustrativo.

## Pipeline
1. Objetivo pedagógico en una frase. Lee el documento de verdad (`inventory` no extrae PDF: léelo y cita la página).
2. Datos: `universal/datos.py` como modelo. Calcula en Python, guarda la procedencia (URL, fecha, sha256).
3. Guion con las cifras calculadas. Voz con `python -m universal.cli voice`.
4. Escenas sobre el inicio de cada frase: `build_props` en `datos.py`.
5. `Explainer-Landscape` o `Explainer-Reel`. Modelo completo: `universal/demos.py` → `demo_explainer`.

## Piezas disponibles (`template/src/universal/explainer/piezas.tsx`)
`ConceptReveal`, `DataChart`, `Comparison`, `Timeline`, `FlowDiagram`, `StepByStepExplainer`, `FichaFuente`.

Mapas y vistas explosionadas: no construidos en Remotion, bloques HyperFrames `world-map`, `us-map`, `exploded-stack` (`hyperframes-registry`).
Manim y Motion Canvas no se adoptaron: ver `docs/THIRD-PARTY.md`.

## Tono
Calma permitida. Sin CTA comercial impuesto. Declara las tenues largas en `quality.exceptions` (`freeze`).

## Versión web
`python -m universal.cli infographic -c examples/universal/infographic.json -o out/info.html`
