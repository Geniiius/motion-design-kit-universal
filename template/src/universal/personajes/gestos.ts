import { Easing, interpolate } from "remotion";

// Todo es función pura del tiempo: se puede renderizar cualquier fotograma en cualquier orden.
export type Marca = { id: number; start: number; duration: number };
export type Gesto = { tipo: "saludar" | "senalar" | "asentir" | "reaccionar" | "contar" | "saltar"; inicio: number; fin: number; lado?: 1 | -1 };
export type Boca = { abre: number; ancho: number };

// Visemas SAPI 0-21 -> forma de boca [abertura, anchura]
const FORMAS: [number, number][] = [
  [0.02, 0.62], [0.55, 0.8], [0.85, 0.82], [0.72, 0.62], [0.5, 0.92], [0.42, 0.7], [0.3, 1], [0.28, 0.36], [0.6, 0.42], [0.8, 0.75], [0.62, 0.5],
  [0.72, 0.85], [0.38, 0.78], [0.3, 0.58], [0.3, 0.72], [0.14, 0.85], [0.2, 0.55], [0.18, 0.72], [0.1, 0.72], [0.18, 0.78], [0.3, 0.72], [0.02, 0.6],
];

const suave = Easing.bezier(0.45, 0, 0.25, 1);
const mezcla = (a: number, b: number, p: number) => a + (b - a) * p;

export const bocaEn = (t: number, visemas: Marca[], envolvente: number[] = []): Boca => {
  if (visemas.length) {
    let i = -1;
    for (let k = 0; k < visemas.length; k++) if (visemas[k].start <= t) i = k;
    if (i < 0) return { abre: 0.02, ancho: 0.62 };
    const v = visemas[i];
    const sig = visemas[i + 1];
    const a = FORMAS[v.id] ?? FORMAS[0];
    if (t > v.start + Math.max(v.duration, 0.01) + 0.08) return { abre: 0.02, ancho: 0.62 };
    if (!sig) return { abre: a[0], ancho: a[1] };
    const b = FORMAS[sig.id] ?? FORMAS[0];
    const p = interpolate(t, [sig.start - 0.045, sig.start + 0.01], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return { abre: mezcla(a[0], b[0], p), ancho: mezcla(a[1], b[1], p) };
  }
  // Sin visemas: repliegue a la amplitud de la voz
  const amp = envolvente[Math.floor(t * 30)] ?? 0;
  return { abre: amp * 0.8, ancho: 0.62 + amp * 0.2 };
};

export type Pose = {
  x: number; y: number; giro: number; inclina: number; salto: number; aplasta: number;
  manoD: [number, number, number]; manoI: [number, number, number]; rotD: number; rotI: number;
  ceja: number; ojos: number; mira: [number, number];
};

const env = (t: number, g: Gesto) =>
  interpolate(t, [g.inicio, g.inicio + 0.28, g.fin - 0.26, g.fin], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: suave });

export const poseEn = (t: number, gestos: Gesto[], hablando: number): Pose => {
  const respira = Math.sin(t * 2.1);
  const p: Pose = {
    x: 0, y: 0.04 * respira, giro: Math.sin(t * 0.6) * 0.06 + hablando * Math.sin(t * 2.7) * 0.05, inclina: Math.sin(t * 0.9) * 0.015 + hablando * Math.sin(t * 3.3) * 0.02,
    salto: 0, aplasta: 1 + respira * 0.008,
    manoD: [1.32, -0.28 + 0.04 * Math.sin(t * 2.3), 0.28], manoI: [-1.32, -0.28 + 0.04 * Math.sin(t * 2.3 + 1), 0.28], rotD: -0.25, rotI: 0.25,
    ceja: 0, ojos: 1, mira: [Math.sin(t * 0.37) * 0.015, Math.sin(t * 0.5) * 0.01],
  };
  const blink = (t * 0.41) % 1;
  if (blink > 0.955) p.ojos = 0.12;
  // Las manos acompañan al habla, sin gesticular de más
  p.manoD[1] += hablando * Math.sin(t * 4.1) * 0.05;
  p.manoI[1] += hablando * Math.sin(t * 3.6 + 2) * 0.05;
  for (const g of gestos) {
    const e = env(t, g);
    if (e <= 0) continue;
    const u = t - g.inicio;
    const lado = g.lado ?? 1;
    const mano = lado > 0 ? p.manoD : p.manoI;
    if (g.tipo === "saludar") {
      mano[0] = mezcla(mano[0], lado * 1.28, e);
      mano[1] = mezcla(mano[1], 0.92, e);
      mano[2] = mezcla(mano[2], 0.42, e);
      const r = Math.sin(u * 11) * 0.42 * e;
      if (lado > 0) p.rotD = mezcla(p.rotD, r, e); else p.rotI = mezcla(p.rotI, r, e);
      p.inclina += -lado * 0.05 * e;
      p.ceja += 0.5 * e;
    } else if (g.tipo === "senalar") {
      mano[0] = mezcla(mano[0], lado * 1.86, e);
      mano[1] = mezcla(mano[1], 0.3, e);
      mano[2] = mezcla(mano[2], 0.62, e);
      p.giro += lado * 0.3 * e;
      p.mira = [lado * 0.05 * e, p.mira[1]];
      if (lado > 0) p.rotD = mezcla(p.rotD, -1.45, e); else p.rotI = mezcla(p.rotI, 1.45, e);
    } else if (g.tipo === "asentir") {
      p.inclina += Math.sin(u * 8) * 0.02 * e;
      p.aplasta += Math.sin(u * 8) * 0.03 * e;
      p.y += Math.sin(u * 8) * 0.05 * e;
    } else if (g.tipo === "reaccionar") {
      p.ceja += 1 * e;
      p.aplasta += 0.05 * e;
      p.y += 0.14 * e;
      p.manoD[1] = mezcla(p.manoD[1], 0.55, e);
      p.manoI[1] = mezcla(p.manoI[1], 0.55, e);
      p.manoD[0] = mezcla(p.manoD[0], 1.58, e);
      p.manoI[0] = mezcla(p.manoI[0], -1.58, e);
    } else if (g.tipo === "contar") {
      mano[0] = mezcla(mano[0], lado * 1.2, e);
      mano[1] = mezcla(mano[1], 0.5 + Math.abs(Math.sin(u * 5)) * 0.2, e);
    } else if (g.tipo === "saltar") {
      const q = Math.sin(Math.min(1, u / (g.fin - g.inicio)) * Math.PI);
      p.salto += q * 0.32;
      p.aplasta += (q > 0.5 ? 0.04 : -0.08) * e;
    }
  }
  return p;
};
