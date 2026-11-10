---
name: cinematic-3d
description: "Escenas 3D con lenguaje de cine y composición de rodaje + 3D: cámara separada del mundo, luz de entorno, bandas 2,39:1, etalonaje. Composiciones Escena3D-* e Hibrido-*. Usar para looks cinematográficos, vitrinas de producto 3D o vídeo real con elementos 3D."
---

# Cine 3D

**Lo que se alcanza aquí es un look de cine en 3D PBR, no fotorrealismo.** El fotorrealismo exige Blender y buenos assets, o un proveedor externo. Dilo antes de empezar.

## Composiciones
- `Escena3D-*`: objeto héroe, halos, suelo pulido, bandas. Props: `titulo`, `subtitulo`, `cinemascope`.
- `Hibrido-*`: rodaje con `OffthreadVideo` + personaje 3D con fondo transparente. Sin seguimiento de cámara: si la toma se mueve, el 3D no la sigue.

## Reglas que dan calidad
1. **Luz de entorno siempre** (`Entorno`): sin reflejos, el 3D se ve plano.
2. **La cámara es una pista aparte** (`Camara`, `Toma[]`): plano general, medio, primer plano, mismos personajes.
3. Materiales físicos con `clearcoat` en lo brillante. Luz motivada, contraluz.
4. Plantilla de storyboard y leyes: `docs/STORYBOARD-AGENCY.md`.

## Rendimiento
GPU con ANGLE; si falla, repliegue automático a `swangle` (CPU, más lento). Trabaja en `draft`, valida con `review`, entrega en `final`.

Todo debe calcularse desde `t`: nada de `Math.random` sin semilla ni estado entre fotogramas.
