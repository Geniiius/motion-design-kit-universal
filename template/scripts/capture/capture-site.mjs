// Captura una web con Playwright para usarla en un vídeo promocional.
// Genera: captura de la parte superior, captura de página completa y vídeo de scroll suave.
//
// Uso:
//   npm run capture -- https://ejemplo.com
//   npm run capture -- https://ejemplo.com --format reel --name landing --scroll 6
// Formatos: reel (1080x1920 en móvil) | landscape (1920x1080) | square (1080x1080)

import { chromium, devices } from "playwright";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const url = args.find((a) => /^https?:\/\//.test(a));
const opt = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
if (!url) {
  console.error("Uso: npm run capture -- <url> [--format reel|landscape|square] [--name nombre] [--scroll segundos]");
  process.exit(1);
}

const format = opt("format", "landscape");
const name = opt("name", new URL(url).hostname.replace(/\W+/g, "-"));
const scrollSeconds = Number(opt("scroll", 5));
const outDir = path.resolve("public/captures");
fs.mkdirSync(outDir, { recursive: true });

// Viewport CSS + deviceScaleFactor => imágenes nítidas a la resolución del vídeo
const presets = {
  reel: { ...devices["iPhone 13"], viewport: { width: 390, height: 693 }, deviceScaleFactor: 1080 / 390 },
  landscape: { viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 },
  square: { viewport: { width: 720, height: 720 }, deviceScaleFactor: 1.5 },
};
const ctxOpts = presets[format] ?? presets.landscape;
const { width, height } = ctxOpts.viewport;

const browser = await chromium.launch();

// 1) Capturas
{
  const ctx = await browser.newContext(ctxOpts);
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(outDir, `${name}-${format}.png`) });
  await page.screenshot({ path: path.join(outDir, `${name}-${format}-full.png`), fullPage: true });
  await ctx.close();
}

// 2) Vídeo de scroll (easing suave, sin tirones)
{
  const ctx = await browser.newContext({
    ...ctxOpts,
    deviceScaleFactor: 1,
    recordVideo: { dir: outDir, size: { width, height } },
  });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1000);
  await page.evaluate(async (ms) => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const start = performance.now();
    const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
    await new Promise((resolve) => {
      const step = (now) => {
        const t = Math.min(1, (now - start) / ms);
        window.scrollTo(0, max * ease(t));
        t < 1 ? requestAnimationFrame(step) : resolve();
      };
      requestAnimationFrame(step);
    });
  }, scrollSeconds * 1000);
  await page.waitForTimeout(800);
  const video = page.video();
  await ctx.close();
  const target = path.join(outDir, `${name}-${format}-scroll.webm`);
  await video.saveAs(target);
  await video.delete();
}

await browser.close();
console.log(`OK Capturas en public/captures/:
  captures/${name}-${format}.png
  captures/${name}-${format}-full.png
  captures/${name}-${format}-scroll.webm
Consejo: convierte el .webm con scripts/ffmpeg/prepare-footage.ps1 antes de usarlo en Remotion.`);
