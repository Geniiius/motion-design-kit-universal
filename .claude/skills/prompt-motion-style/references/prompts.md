# Plantillas de prompts — estilo Prompt Motion

La estructura que mejor funciona: **entradas** (lo que hay que pedir) → **dirección** (el gusto,
lo prohibido) → **estructura** (el desarrollo, al ritmo de los tiempos) → **construcción** (las
reglas técnicas). Rellenar los `[corchetes]` y pegar en Claude Code abierto en `Motion-Design-Kit/`.

---

## 1. Transformación de UI (look Paper)

```
<entradas>
Producto: [nombre + qué hace en 1 frase]
Estados de UI que debe atravesar la forma (6 a 10): [p. ej. botón → loader → check → tarjeta de datos → toggle → toast → botón]
Acento: [un color] · Formato: [1080x1080 | 1080x1920]
Música (opcional, ~120 BPM): genérala con ElevenLabs o indica la ruta
</entradas>
<direccion>
Motion de UI nivel Dribbble. Una sola forma, nunca un corte: cada estado es el mismo elemento
que cambia de tamaño, radio y color, y su contenido cambia con un desenfoque corto. Un cursor
provoca cada cambio con clics y arrastres reales. Fondo papel gris cálido, componentes negros
y blancos, tipografía Geist. Springs en todo, overshoot mínimo. El último fotograma = el primero.
Prohibido: rebotes exagerados, brillos, degradados en la UI, explosiones de partículas, tiempos muertos, look plantilla.
</direccion>
<estructura>
[BPM] BPM, [N] compases, una acción por tiempo: [desarrollo estado por estado]
</estructura>
<construccion>
Usa la skill prompt-motion-style: copia prompt-motion/compositions/paper-ui.html, todo dentro de seek(t),
springs de forma cerrada con PM.track. Verifica con --stills antes del render final.
</construccion>
```

## 2. Showreel de tipografía cinética (look Studio HUD)

```
<entradas>
Marca / persona: [nombre] · Eslogan: [≤ 5 palabras]
Palabras clave que deben golpear (4 a 6, una por tiempo): [palabras] — palabra en acento: [palabra]
Cifra clave: [valor + leyenda]
Formato: 1080x1920 · Duración: [10-15] s · BPM: [120-128]
</entradas>
<direccion>
Showreel de motion designer, 15 s, «a por todas» pero controlado. Fondo negro, un rojo anaranjado,
tipografía gigante Geist 900 con tracking muy ajustado, HUD discreto (esquinas, timecode, etiquetas
mono diminutas). Un punto que respira al tempo → se divide → destello → palabras → dato → logo →
vuelta al punto (bucle).
Prohibido: brillos, degradados, más de un color de acento, fundidos encadenados.
</direccion>
<estructura>
Tiempos 1-4: señal (punto) · 5-6: destello · 7-10: una palabra por tiempo · 11-14: cifra + anillo · 15-20: logo → punto.
</estructura>
<construccion>
Skill prompt-motion-style, base prompt-motion/compositions/studio-hud.html. Render --stills y luego MP4.
Música: skill music de ElevenLabs al BPM indicado.
</construccion>
```

## 3. Promo de producto / anuncio (híbrido)

```
<entradas>
Producto + URL: [..] (captura la web con la skill playwright-capture)
Beneficios (3): [..] · Prueba: [cifra, logo de cliente, opinión] · CTA: [..]
Formatos: 9:16 + 1:1 · Duración: 15 s · Voz en off: [sí/no, tono, idioma]
</entradas>
<direccion>
Look Paper: capturas reales del producto en un marco de navegador/móvil, el cursor muestra el uso,
cada beneficio = una transformación de la UI, prueba con contador, final con logo + CTA. Un color de acento.
</direccion>
<estructura>
Hook (2 s, problema en ≤ 6 palabras) → 3 beneficios (3 s cada uno, uno por compás) → prueba (2 s) → CTA (2 s, = fotograma inicial).
</estructura>
<construccion>
seek(t) + springs de forma cerrada, una sola forma principal, voz con text-to-speech de ElevenLabs,
verificar los fotogramas antes del render.
</construccion>
```

## 4. Diagrama / explicación

```
<entradas>Concepto: [..] · Pasos (3 a 6): [..] · Formato: 16:9 · Voz en off: [sí/no]</entradas>
<direccion>
Fondo papel, trazos negros finos que se dibujan (stroke-dashoffset), nodos que aparecen con spring,
anotaciones manuscritas azules con flechas, un solo elemento en acento: el camino importante.
Cámara que hace zoom en cada paso y luego se aleja para revelar el conjunto.
</direccion>
<construccion>SVG dentro de un HTML seek(t), cámara = transform scale/translate de un grupo padre con PM.track.</construccion>
```

## 5. El prompt «showreel» original (una línea)

El más usado en el sitio; lanzarlo tal cual y luego iterar:

```
Haz un vídeo de motion graphics dinámico de 15 segundos que demuestre lo increíble que eres
como motion designer, como si fuera tu showreel para un currículum. Dalo todo.
Usa la skill prompt-motion-style.
```

Consejos para iterar: «haz cada transición más precisa», «cuadra todo con el tiempo musical»,
«elimina todo lo que parezca plantilla», «enséñame 6 fotogramas antes de renderizar».
