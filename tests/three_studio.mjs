// Aperçu 3D interactif (modules/three-studio) : construit, ouvert dans Chromium, boutons cliqués.
//   node tests/three_studio.mjs <copie-du-module> <image-preuve>
import { createRequire } from "node:module";
import { spawn, spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = createRequire(path.join(here, "..", "prompt-motion", "package.json"))("playwright");
const [dir, proof] = process.argv.slice(2);
const npm = process.platform === "win32" ? "npm.cmd" : "npm";
const run = (args) => {
  const r = spawnSync(npm, args, { cwd: dir, shell: process.platform === "win32", encoding: "utf8" });
  if (r.status !== 0) throw new Error(`npm ${args.join(" ")}: ${(r.stderr || r.stdout).slice(-400)}`);
};
run(["install", "--no-fund", "--no-audit", "--save-exact"]);
run(["run", "build"]);
const server = spawn(npm, ["run", "preview", "--", "--port", "4179", "--strictPort"], { cwd: dir, shell: process.platform === "win32" });
let code = 1;
try {
  await new Promise((r) => setTimeout(r, 2500));
  const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
  const page = await browser.newPage({ viewport: { width: 1100, height: 700 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto("http://127.0.0.1:4179/");
  await page.waitForSelector("canvas");
  await page.click("#wave");
  await page.click("#turn");
  await page.waitForTimeout(800);
  await page.screenshot({ path: proof });
  const size = await page.evaluate(() => document.querySelector("canvas").width);
  console.log(`canvas ${size}px, erreurs: ${errors.length} ${errors.join(" ").slice(0, 200)}`);
  code = size > 0 && errors.length === 0 ? 0 : 1;
  await browser.close();
} finally {
  if (process.platform === "win32") spawnSync("taskkill", ["/pid", String(server.pid), "/f", "/t"]);
  else server.kill();
}
process.exit(code);
