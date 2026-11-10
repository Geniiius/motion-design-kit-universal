// Vrais clics, vrai clavier, vrai toucher dans un vrai navigateur. Sortie != 0 si un test échoue.
//   node tests/deck.spec.mjs <deck.html> <dossier-preuves>
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, "..", "prompt-motion", "package.json"));
const { chromium } = require("playwright");

const [deck, proofs] = process.argv.slice(2);
fs.mkdirSync(proofs, { recursive: true });
const url = pathToFileURL(path.resolve(deck)).href;
const results = [];
const check = async (name, fn) => {
  try {
    await fn();
    results.push({ name, status: "PASS" });
  } catch (e) {
    results.push({ name, status: "FAIL", error: String(e.message).slice(0, 200) });
  }
};
const expect = (ok, msg) => {
  if (!ok) throw new Error(msg);
};

const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
const external = [];
page.on("request", (r) => {
  if (!r.url().startsWith("file:") && !r.url().startsWith("data:")) external.push(r.url());
});
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
await page.goto(url);

await check("menu visible au chargement", async () => {
  expect(await page.locator("#menu").isVisible(), "menu caché");
  expect((await page.locator(".tile").count()) === 5, "5 services attendus");
});
await page.screenshot({ path: path.join(proofs, "1-menu.png") });

await check("vrai clic: ouvre un service et met à jour l'adresse", async () => {
  await page.locator('[data-open="1"]').click();
  expect(await page.locator("#detail-1").isVisible(), "détail 2 caché");
  expect(!(await page.locator("#menu").isVisible()), "menu encore visible");
  expect(page.url().endsWith("#service-2"), "hash non mis à jour");
});

await check("démo par étapes: chaque clic révèle l'étape suivante", async () => {
  const steps = page.locator("#detail-1 .steps li");
  const button = page.locator("#detail-1 [data-next-step]");
  expect((await page.locator("#detail-1 .steps li.on").count()) === 0, "étape déjà active");
  await button.click();
  await button.click();
  expect((await page.locator("#detail-1 .steps li.on").count()) === 2, "2 étapes attendues");
  expect((await steps.count()) === 3, "3 étapes attendues");
});
await page.screenshot({ path: path.join(proofs, "2-etapes.png") });

await check("clavier: flèche droite passe au service suivant", async () => {
  await page.keyboard.press("ArrowRight");
  expect(await page.locator("#detail-2").isVisible(), "service 3 non affiché");
});

await check("point interactif: le clic affiche sa note", async () => {
  await page.locator("#detail-2 .pin").nth(1).click();
  const note = await page.locator("#detail-2 .note").textContent();
  expect(note.includes("Lumière"), `note inattendue: ${note}`);
  expect((await page.locator("#detail-2 .pin").nth(1).getAttribute("aria-pressed")) === "true", "aria-pressed absent");
});
await page.screenshot({ path: path.join(proofs, "3-points.png") });

await check("Échap: retour au menu et focus rendu au bon bouton", async () => {
  await page.keyboard.press("Escape");
  expect(await page.locator("#menu").isVisible(), "menu non revenu");
  const focused = await page.evaluate(() => document.activeElement?.getAttribute("data-open"));
  expect(focused === "2", `focus sur ${focused}`);
});

await check("chapitres: le bouton courant est signalé", async () => {
  await page.locator('[data-chapter="1"]').click();
  expect(await page.locator("#detail-0").isVisible(), "chapitre non ouvert");
  expect((await page.locator('[data-chapter="1"]').getAttribute("aria-current")) === "true", "aria-current absent");
});

await check("avant/après: le curseur répond au clavier", async () => {
  const range = page.locator("#detail-0 .compare input");
  await range.focus();
  for (let i = 0; i < 10; i++) await page.keyboard.press("ArrowRight");
  const pos = await page.locator("#detail-0 .compare").evaluate((e) => e.style.getPropertyValue("--pos"));
  expect(pos === "60%", `position ${pos}`);
  await page.keyboard.press("Tab");
});
await page.screenshot({ path: path.join(proofs, "4-avant-apres.png") });

await check("lien direct: #service-4 ouvre le bon service", async () => {
  const p2 = await browser.newPage();
  await p2.goto(url + "#service-4");
  expect(await p2.locator("#detail-3").isVisible(), "service 4 non ouvert");
  await p2.close();
});

await check("Tab atteint les commandes, focus visible", async () => {
  const p2 = await browser.newPage();
  await p2.goto(url);
  await p2.keyboard.press("Tab");
  const tag = await p2.evaluate(() => document.activeElement?.tagName);
  expect(tag === "BUTTON", `focus sur ${tag}`);
  await p2.close();
});

await check("toucher + téléphone: pas de défilement horizontal, cibles de 44 px", async () => {
  const ctx = await browser.newContext({ viewport: { width: 375, height: 760 }, hasTouch: true, isMobile: true });
  const p2 = await ctx.newPage();
  await p2.goto(url);
  const overflow = await p2.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow <= 0, `débordement ${overflow}px`);
  await p2.screenshot({ path: path.join(proofs, "5-telephone.png"), fullPage: false });
  await p2.locator('[data-open="0"]').tap();
  expect(await p2.locator("#detail-0").isVisible(), "tap sans effet");
  const small = await p2.evaluate(() => [...document.querySelectorAll("button")].filter((b) => b.offsetParent && (b.offsetHeight < 44 || b.offsetWidth < 44)).length);
  expect(small === 0, `${small} bouton(s) trop petits`);
  const overflow2 = await p2.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow2 <= 0, `débordement détail ${overflow2}px`);
  await p2.screenshot({ path: path.join(proofs, "6-telephone-detail.png"), fullPage: false });
  await ctx.close();
});

await check("mouvement réduit: animations coupées", async () => {
  const ctx = await browser.newContext({ reducedMotion: "reduce" });
  const p2 = await ctx.newPage();
  await p2.goto(url);
  await p2.locator('[data-open="0"]').click();
  const anim = await p2.locator("#detail-0").evaluate((e) => getComputedStyle(e).animationName);
  expect(anim === "none", `animation ${anim}`);
  await ctx.close();
});

await check("aucune requête réseau, aucune erreur JavaScript", async () => {
  expect(external.length === 0, `requêtes: ${external.join(", ")}`);
  expect(errors.length === 0, `erreurs: ${errors.join("; ")}`);
});

await browser.close();
fs.writeFileSync(path.join(proofs, "interactions.json"), JSON.stringify(results, null, 2));
for (const r of results) console.log(`${r.status}  ${r.name}${r.error ? " : " + r.error : ""}`);
process.exit(results.some((r) => r.status !== "PASS") ? 1 : 0);
