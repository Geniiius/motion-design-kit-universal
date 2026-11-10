// Renderiza una composición Prompt Motion (HTML + seek(t)) en MP4.
// Playwright llama a seek(t) fotograma a fotograma, captura y envía las imágenes a ffmpeg.
//
//   node render.mjs compositions/paper-ui.html
//   node render.mjs compositions/studio-hud.html --audio ../template/public/audio/musica/pista.mp3 --out out/reel.mp4
//   node render.mjs compositions/paper-ui.html --from 2 --to 4      (fragmento)
//   node render.mjs compositions/paper-ui.html --stills 0,1.6,3.2   (PNG de control)

import { chromium } from "playwright";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const file = args.find((a) => a.endsWith(".html"));
const opt = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
if (!file) {
  console.error("Uso: node render.mjs <composicion.html> [--out f.mp4] [--audio m.mp3] [--from s] [--to s] [--stills 0,1.5]");
  process.exit(1);
}

const name = path.basename(file, ".html");
fs.mkdirSync("out", { recursive: true });
const out = opt("out", `out/${name}.mp4`);

const browser = await chromium.launch();
const page = await browser.newPage();
await page.addInitScript(() => { window.__RENDERING__ = true; });
await page.goto(pathToFileURL(path.resolve(file)).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
const comp = await page.evaluate(() => window.COMP);
if (!comp) throw new Error("La composición debe definir window.COMP y window.seek(t)");
await page.setViewportSize({ width: comp.width, height: comp.height });

// --- Imágenes de control ---
const stills = opt("stills", "");
if (stills) {
  for (const s of stills.split(",").map(Number)) {
    await page.evaluate((t) => window.seek(t), s);
    const png = `out/${name}-${s.toFixed(2)}s.png`;
    await page.screenshot({ path: png });
    console.log("OK", png);
  }
  await browser.close();
  process.exit(0);
}

// --- Vídeo ---
const from = Number(opt("from", 0));
const to = Number(opt("to", comp.duration));
const total = Math.round((to - from) * comp.fps);
const audio = opt("audio", "");

const ff = spawn("ffmpeg", [
  "-y", "-v", "error",
  "-f", "image2pipe", "-framerate", String(comp.fps), "-c:v", "mjpeg", "-i", "-",
  ...(audio ? ["-ss", String(from), "-i", audio, "-af", `afade=t=out:st=${Math.max(0, to - from - 1)}:d=1`, "-shortest"] : []),
  "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
  "-vf", "scale=out_range=tv,format=yuv420p", "-color_range", "tv",
  ...(audio ? ["-c:a", "aac", "-b:a", "192k"] : []),
  "-movflags", "+faststart", out,
], { stdio: ["pipe", "inherit", "inherit"] });

const started = Date.now();
for (let i = 0; i < total; i++) {
  const t = from + i / comp.fps;
  await page.evaluate((tt) => window.seek(tt), t);
  const buf = await page.screenshot({ type: "jpeg", quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  if (i % comp.fps === 0) process.stdout.write(`\r  fotograma ${i}/${total}`);
}
ff.stdin.end();
await new Promise((r, j) => ff.on("close", (code) => (code === 0 ? r() : j(new Error(`ffmpeg código ${code}`)))));
await browser.close();
console.log(`\rOK ${out}  (${total} fotogramas, ${((Date.now() - started) / 1000).toFixed(1)} s)`);
