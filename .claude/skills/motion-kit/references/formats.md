# Formatos por plataforma (2026)

| Plataforma | Formato | Resolución | Duración recomendada | Zonas tapadas / notas |
|---|---|---|---|---|
| Instagram Reels | 9:16 | 1080×1920 | 7–30 s (máx. 3 min) | Arriba 14 %, abajo 20 %, derecha 12 % |
| TikTok | 9:16 | 1080×1920 | 9–34 s | Abajo 20 % (texto), derecha 15 % (botones) |
| YouTube Shorts | 9:16 | 1080×1920 | 15–45 s (máx. 3 min) | Abajo 18 % |
| Stories (IG/FB) | 9:16 | 1080×1920 | ≤ 15 s por story | Arriba 14 %, abajo 18 % |
| Feed IG / FB / LinkedIn | 4:5 | 1080×1350 | 15–45 s | Ocupa más pantalla en el feed |
| Cuadrado (anuncios, carrusel) | 1:1 | 1080×1080 | 6–30 s | Compatible en todas partes |
| YouTube, web, presentación | 16:9 | 1920×1080 | 30 s – 2 min | 4K posible: `--scale=2` |
| Anuncio bumper YouTube | 16:9 | 1920×1080 | 6 s exactos | 1 mensaje, 1 logo |
| Vídeo nativo LinkedIn | 4:5 o 1:1 | — | 30–90 s | 80 % se ve sin sonido → subtítulos obligatorios |

Composiciones del template por formato: `*-Reel` (9:16), `*-Feed` (4:5), `*-Square` (1:1), `*-Landscape` (16:9).

## Especificaciones técnicas comunes
- 30 fps (60 solo para movimientos muy rápidos / gaming)
- H.264 High, yuv420p, AAC 48 kHz, `+faststart`
- Música a ≈ −14 LUFS, voz por encima de la música (ducking)
- Siempre subtítulos: la mayoría ve los vídeos sin sonido
