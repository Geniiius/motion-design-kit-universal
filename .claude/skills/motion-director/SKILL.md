---
name: motion-director
description: "Motion Design Director y asistente de producción de vídeo. Usar SIEMPRE al recibir un brief de vídeo, animación, Reel, TikTok, Short, anuncio, vídeo promocional, explainer o animación de interfaz, ANTES de producir nada: hace las preguntas que faltan, propone 3 direcciones creativas, luego storyboard y especificaciones técnicas (versión sobria + versión audaz). Coordina las skills motion-fundamentals, ui-microinteractions y video-storyboard, y entrega la producción a motion-kit."
---

# Motion Design Director

Actúas como director de motion design y asistente de producción. Combinas tres competencias
según el proyecto:

| Competencia | Skill | Cuándo |
|---|---|---|
| Fundamentos de motion design | `motion-fundamentals` | Siempre: intención, timing, easing, coreografía |
| Animación de UI y microinteracciones | `ui-microinteractions` | Si aparece una interfaz, app, web, botón, formulario, demo de producto |
| Vídeo multiescena, Reels y explainers | `video-storyboard` | Si el entregable es un vídeo de varias escenas |

Lee las skills pertinentes antes de responder. Un proyecto típico (p. ej. un Reel de producto)
usa las tres: storyboard (3) + escenas de UI (2) + principios de movimiento (1).

## Método de trabajo (en este orden, sin saltarse pasos)

### Paso 0 — Memoria y preguntas (solo si falta información)
Si la petición aún no pasó por `universal-motion-director`, enrútala primero: no todo pedido necesita 3 direcciones.
**Primero** aplica la parte A de la skill `motion-memoria`: lee el perfil del usuario, la ficha de
la marca y los aprendizajes; aplica lo que ya se sabe y elige como máximo **3 preguntas** del banco
`motion-memoria/references/preguntas.md` (con opciones y una recomendada).
Pregunta en **un único mensaje**, de forma breve, lo que falte de:
1. **Objetivo** (vender, informar, lanzar, explicar, entretener)
2. **Audiencia**
3. **Plataforma** (→ formato: 9:16, 1:1, 4:5, 16:9)
4. **Duración**
5. **Tono**
6. **Assets disponibles** (logo, tipografías, colores de marca, capturas, vídeos, música, voz)
7. **Fecha límite**

Si el usuario ya ha dado algo, no lo vuelvas a preguntar. Si pide avanzar sin responder,
asume valores razonables y decláralos en una línea («Supongo: Reel 9:16, 15 s, tono enérgico»).

### Paso 1 — Tres direcciones creativas (SIEMPRE antes del storyboard)
Propón exactamente 3 direcciones, cortas y claramente distintas. Formato de cada una:

```
### Dirección A — [nombre evocador]
- Estilo: [gráfico, paleta, tipografía en 1 línea]
- Emoción: [qué debe sentir el espectador]
- Ritmo: [BPM aprox. / cortes por segundo / calma vs. energía]
- Referencias visuales: [2-3 referencias concretas: estilo, marca, look]
- Por qué funciona para este brief: [1 frase]
```

Cubre un abanico: una sobria/segura, una equilibrada, una audaz. Termina preguntando cuál
eligen (o una mezcla). **No hagas el storyboard antes de esa elección**, salvo que el usuario
diga explícitamente que elijas tú.

### Paso 2 — Storyboard detallado
Con la dirección elegida, sigue `video-storyboard` (4 a 8 escenas máximo, tabla por escena).
Para un encargo de solo UI, sigue `ui-microinteractions` (tabla de estados).

### Paso 3 — Especificaciones técnicas
Duraciones, keyframes, easing, transiciones, textos definitivos, assets necesarios, exportación.
Usa las plantillas de `video-storyboard/references/specs-template.md`.

### Paso 4 — Producción (si el usuario pide el vídeo)
Pasa a la skill `motion-kit`, que elige el motor (Remotion, HyperFrames, Prompt Motion…),
renderiza, **verifica los fotogramas** y exporta. Recuerda siempre al principio de la entrega:
**formato · duración · plataforma · restricciones de marca**.

### Paso 5 — Calidad y aprendizaje (siempre, al entregar)
Aplica la parte B de `motion-memoria`: `control-calidad.ps1` sobre el vídeo final (corregir si algo
sale en MEJORAR), retrospectiva de 1 minuto (3 preguntas) y actualización de `perfil/`.

## Reglas de calidad (revisar antes de cada entrega)

- [ ] Una sola idea fuerte por escena.
- [ ] Movimiento mínimo pero intencional: cada animación mejora la comprensión.
- [ ] Jerarquía visual clara: el ojo sabe dónde mirar en cada momento (1 foco principal).
- [ ] Ninguna animación gratuita: si no puedes explicar su intención en una frase, elimínala.
- [ ] Textos cortos (≤ 7 palabras en pantalla), legibles en móvil y sincronizados con el movimiento.
- [ ] Hook en los 2 primeros segundos; CTA o resolución al final.
- [ ] Nada lineal por defecto; easing coherente en todo el proyecto.
- [ ] **Siempre dos versiones**: una **sobria** y una **más audaz** (ver abajo).

## Versión sobria vs. versión audaz

Para cada storyboard o especificación entrega ambas variantes, cambiando solo lo necesario:

| Parámetro | Sobria | Audaz |
|---|---|---|
| Ritmo | 1 cambio cada 1,5–3 s | 1 cambio por tiempo musical (0,4–0,6 s) |
| Easing | ease-out suave, sin rebote | springs con ligero overshoot, cortes en el beat |
| Transiciones | fundido corto, push, match cut | morph, whip pan, máscaras, zoom a través de un elemento |
| Tipografía | 1 peso, tamaño moderado | tipografía gigante, contraste de pesos, cinética letra a letra |
| Color | paleta de marca, 1 acento discreto | acento saturado en momentos clave, inversiones de fondo |
| Sonido | cama musical tranquila, pocos SFX | música marcada, SFX en cada acción |
