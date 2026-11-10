---
name: playwright-capture
description: "Capturar una web o una aplicación web con Playwright para usarla en un vídeo promocional / motion design: capturas en alta resolución (móvil 9:16, escritorio 16:9, cuadrado), página completa, vídeo de scroll suave, grabación de un recorrido de usuario (clics, escritura). Usar cuando se quiera mostrar una web, un SaaS, una app o una landing page en un vídeo, o hacer una demo de producto animada."
---

# Captura de webs con Playwright

## Captura rápida (script del kit)

Desde `template/`:

```bash
npm run capture -- https://ejemplo.com --format reel --name landing --scroll 6
```

- `--format`: `reel` (iPhone, 1080 px de ancho) · `landscape` (1280×720 @1.5x) · `square`
- Genera en `public/captures/`: `<nombre>-<formato>.png`, `<nombre>-<formato>-full.png`, `<nombre>-<formato>-scroll.webm`
- Antes de usar el vídeo en Remotion, normalizarlo:
  `.\scripts\ffmpeg\prepare-footage.ps1 public\captures\landing-reel-scroll.webm -Formato reel`
  → `media: "footage/landing-reel-scroll-reel.mp4"` en las props de una escena `Promo`.

Alternativa HyperFrames: `npx hyperframes capture <url>`.

## Usar una captura de página completa en Remotion

La mejor demo no suele ser el vídeo de scroll sino la captura `-full.png` animada en Remotion
(control total del easing): ponerla dentro de un marco de móvil / navegador y animar
`translateY` de 0 a `-(altoImagen - altoMarco)` con `interpolate` + `theme.easing.inOut`,
con pausas en las secciones clave. Añadir una ligera escala 1→1,04 y una sombra.

## Recorrido de usuario con guion (demo de SaaS)

Para grabar interacciones, escribir un script junto a `scripts/capture/capture-site.mjs`:

```js
import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  recordVideo: { dir: "public/captures", size: { width: 1280, height: 720 } },
});
const page = await ctx.newPage();
await page.goto("http://localhost:3000");
await page.getByRole("button", { name: "Crear proyecto" }).click();
await page.getByLabel("Nombre").pressSequentially("Lanzamiento Q4", { delay: 80 }); // escritura visible
await page.waitForTimeout(1200); // dejar respirar cada paso
await ctx.close(); // el vídeo se guarda al cerrar el contexto
await browser.close();
```

Consejos:
- `pressSequentially(..., { delay: 60–100 })` para una escritura natural; `waitForTimeout` de 800–1500 ms entre pasos.
- Ocultar banners de cookies / chats: `await page.addStyleTag({ content: "#cookie-banner,.intercom-launcher{display:none!important}" })`.
- Modo oscuro: `browser.newContext({ colorScheme: "dark" })`.
- Nunca escribir credenciales reales en un script de captura: usar una cuenta de demo / datos ficticios.
- Si falta Chromium: `npx playwright install chromium`.
