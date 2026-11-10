# Reglas de diseño — color, tipografía, ritmo, sonido, checklist

## Sistema de color
Una base oscura (o clara) + UN color protagonista + un acento + neutros. Regla 60/30/10:
60 % base, 30 % superficies secundarias, 10 % protagonista. El color protagonista aparece
COMO MÁXIMO en un elemento por fotograma: dirige la mirada.

Paletas probadas (adaptar a la marca si existe):
- Tech oscuro: base #0A0A0F, protagonista #7C3AED, acento #22D3EE, texto #F4F4F5
- Editorial cálido: base #FAF7F2, protagonista #D97757, tinta #1F1E1B
- Premium cálido: base #1A120B, protagonista #E8A33D, acento #F4E9DA
- Claro limpio: base #F7F5F2, tinta #1A1A1A + un acento saturado

Brillo solo en el elemento protagonista:
`boxShadow: 0 0 60px ${hero}66, 0 0 120px ${hero}33` (texto: textShadow).
Más de un elemento brillante por fotograma = Las Vegas. No.

## Tipografía
- Titulares: fuente display (Clash Display, Cabinet Grotesk, General Sans, Satoshi — gratis en
  Fontshare; o una Google variable font con @remotion/google-fonts).
  Peso 600–800, letterSpacing -0.03em, lineHeight 1.05.
- Tamaño de titular en Reels: 80–140 px a 1080 de ancho. Horizontal: 100–160 px a 1920.
- Texto/subtítulos: una sans limpia (Inter) a 400–500, color atenuado.
- Resaltar UNA palabra por titular: color protagonista, subrayado animado o una píldora que
  escala detrás 5 frames después de que aparezca la palabra.
- Números: contadores animados con tabular-nums (ver motion-patterns §9).

## Arquitectura de escenas
Estructura de un Reel de 30 s:
```
0,0–1,5 s  HOOK      el visual más fuerte + promesa. Movimiento en los PRIMEROS 15 frames.
1,5–3,0 s  CONTEXTO  una línea, un visual, sin dejar de moverse.
3–22 s     CUERPO    3–4 bloques. Cada uno: IMPACTO → pausa (15–20 frames quietos) → construcción.
22–27 s    PAYOFF    el resultado / cifra / demo. La animación más grande del vídeo.
27–30 s    CTA       una acción, tranquila, brillo en la palabra del CTA.
```
- Un elemento visual nuevo al menos cada 90 frames.
- Las pausas son una herramienta: movimiento rápido → quietud total → siguiente movimiento.
  El movimiento constante parece amateur; el contraste parece caro.
- Zona segura 9:16: texto crítico en el ~75 % central vertical.
- Firmas de logo de 5 s: símbolo (0–0,8 s) → logotipo (0,6–1,8 s) → detalle/eslogan
  (2–3,5 s) → respiración → salida (últimos 0,5 s).

## Diseño sonoro (50 % de la calidad percibida: nunca entregar en silencio salvo petición)
- Cada IMPACTO de entrada: whoosh/clic corto que empieza 2–3 frames ANTES de que llegue el visual
  (antes = sincronizado; después = roto).
- Transiciones: riser hacia el corte, golpe de bajo EN el corte.
- Contadores: tic suave en bucle mientras cuentan.
- Música de fondo a volumen bajo (~0,2–0,3), más baja aún bajo la voz en off.
- Elegir la música PRIMERO si es posible; calcular framesPorTiempo = fps*60/BPM y cortar en los tiempos.
- Generar música, voz y efectos con las skills de ElevenLabs (`music`, `text-to-speech`,
  `sound-effects`). Un kit de 10 efectos cubre todo: 2 whooshes, 2 clics, riser, golpe de bajo,
  brillo, tic, pop, swoosh inverso.

## Generación de assets (si se generan imágenes para el vídeo)
Fijar un esqueleto de prompt, variar solo el sujeto, mantener idénticas las palabras de luz y
paleta en toda la serie, generar en la relación de aspecto final:
```
[sujeto], fotografía de producto cinematográfica, estudio oscuro, luz de contorno [color],
sombras profundas, poca profundidad de campo, 9:16
```

## Ajustes de render
- Másteres para subir: `--codec h264 --crf 16` (las plataformas recomprimen: dar margen).
- Muchas transparencias/desenfoques: añadir `--image-format png`.
- Revisar movimientos sospechosos a 0,25x en Remotion Studio.

## CHECKLIST ANTES DE ENTREGAR — en cada vídeo
- [ ] Cero easing lineal; cada interpolate con clamp
- [ ] Entradas = 2–3 propiedades, en stagger; nada entra a la vez
- [ ] Salidas animadas, más rápidas que las entradas
- [ ] Cada imagen fija con Ken Burns; movimientos rápidos con motion blur
- [ ] Las 5 capas presentes (fondo, assets, gráficos, etalonaje, grano+viñeta)
- [ ] Un color protagonista, ≤ 1 elemento protagonista/brillante por fotograma
- [ ] Fuente display de peso ≥ 600 en titulares; ningún titular con fuente por defecto
- [ ] Espacios en px (no em) entre bloques de texto grandes
- [ ] Existen pausas: ≥ 3 momentos de quietud
- [ ] Efectos de sonido en los impactos, cortes en el tiempo musical (si hay audio)
- [ ] Texto en zona segura; nada toca los bordes
- [ ] Renderizado, fotogramas extraídos, cada uno revisado, errores corregidos, re-renderizado
