import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Grain } from "../components/Grain";
import { medida, palabrasDe, tema } from "./tema";

export type Palabra = { text: string; start: number; end: number };

// Fondo con dos manchas de luz que derivan: nunca un plano fijo.
export const FondoVivo: React.FC<{ a: string; b: string; c?: string }> = ({ a, b, c }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const x = 30 + Math.sin(t * 0.22) * 18;
  const y = 28 + Math.cos(t * 0.17) * 14;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at ${x}% ${y}%, ${b} 0%, transparent 58%), radial-gradient(ellipse at ${100 - x}% ${100 - y}%, ${c ?? b} 0%, transparent 52%), ${a}`,
      }}
    />
  );
};

export const Acabado: React.FC<{ vineta?: number; grano?: number }> = ({ vineta = 0.42, grano = 0.05 }) => <Grain opacity={grano} vineta={vineta} />;

// Subtítulo palabra a palabra sobre las marcas reales de la voz. La palabra dicha pasa a tinta plena.
export const Subtitulo: React.FC<{ words: Palabra[]; color?: string; apagado?: string; fondo?: string; porFrase?: number }> = ({ words, color = tema.datos.tinta, apagado = "rgba(242,244,250,0.42)", fondo = "rgba(5,8,18,0.55)", porFrase = 44 }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { u, vertical } = medida(width, height);
  const t = frame / fps;
  const i = palabrasDe(words, t);
  if (i < 0 || t > words[words.length - 1].end + 0.25) return null;
  // Trozos: se corta en la puntuación o al llegar al largo máximo, nunca a mitad de palabra
  const trozos: Palabra[][] = [];
  let actual: Palabra[] = [];
  let largo = 0;
  for (const w of words) {
    if (actual.length && largo + w.text.length > porFrase) {
      trozos.push(actual);
      actual = [];
      largo = 0;
    }
    actual.push(w);
    largo += w.text.length + 1;
    if (/[.!?]$/.test(w.text)) {
      trozos.push(actual);
      actual = [];
      largo = 0;
    }
  }
  if (actual.length) trozos.push(actual);
  const trozo = trozos.find((c) => c[0].start - 0.04 <= t && t <= c[c.length - 1].end + 0.2) ?? trozos.find((c) => c.includes(words[i]));
  if (!trozo) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: (vertical ? 400 : 64) * u, pointerEvents: "none" }}>
      <div style={{ maxWidth: "86%", padding: `${12 * u}px ${24 * u}px`, borderRadius: 16 * u, background: fondo, fontFamily: tema.fuentes.body, fontWeight: 600, fontSize: (vertical ? 50 : 42) * u, lineHeight: 1.25, textAlign: "center" }}>
        {trozo.map((w, k) => (
          <span key={k} style={{ color: w.start - 0.04 <= t ? color : apagado, marginRight: 12 * u, display: "inline-block" }}>
            {w.text}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const entrada = (frame: number, inicio: number, fps: number, dur = 0.5) =>
  interpolate(frame, [inicio * fps, (inicio + dur) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: tema.easing.out });

export const salida = (frame: number, fin: number, fps: number, dur = 0.28) =>
  interpolate(frame, [(fin - dur) * fps, fin * fps], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: tema.easing.in });
