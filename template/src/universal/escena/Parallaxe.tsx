import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { Acabado, entrada, salida } from "../capas";
import { medida, tema } from "../tema";

// 2.5D: profundidad simulada con planos que se deslizan a distinta velocidad. No es una escena 3D.
export const parallaxeSchema = z.object({
  fotos: z.array(z.string()).describe("Fotos sueltas: encuadre vivo y paso entre ellas"),
  capas: z.array(z.object({ src: z.string(), profundidad: z.number() })).describe("Planos separados, del fondo al frente: 2.5D real"),
  titulo: z.string(),
  segundosPorFoto: z.number(),
  musica: z.string(),
});
export type ParallaxeProps = z.infer<typeof parallaxeSchema>;
export const parallaxeDefaults: ParallaxeProps = {
  fotos: [],
  capas: [
    { src: "universal/medios/capas/cielo.png", profundidad: 0.1 },
    { src: "universal/medios/capas/lejos.png", profundidad: 0.35 },
    { src: "universal/medios/capas/medio.png", profundidad: 0.65 },
    { src: "universal/medios/capas/frente.png", profundidad: 1 },
  ],
  titulo: "",
  segundosPorFoto: 3,
  musica: "",
};
export const calculateParallaxe: CalculateMetadataFunction<ParallaxeProps> = ({ props }) => ({
  durationInFrames: props.fotos.length ? Math.round(props.fotos.length * props.segundosPorFoto * 30) : 240,
  fps: 30,
});

const Capas: React.FC<{ capas: ParallaxeProps["capas"]; total: number }> = ({ capas, total }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const p = interpolate(frame, [0, total], [0, 1], { extrapolateRight: "clamp", easing: tema.easing.inOut });
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {capas.map((c, i) => (
        <AbsoluteFill key={c.src} style={{ transform: `translateX(${(0.5 - p) * width * 0.12 * c.profundidad}px) translateY(${(0.5 - p) * 24 * c.profundidad}px) scale(${1.18 + p * 0.1 * c.profundidad})`, filter: i === capas.length - 1 ? "blur(2.5px)" : i === 0 ? "blur(1px)" : undefined }}>
          <Img src={staticFile(c.src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
      ))}
    </AbsoluteFill>
  );
};

const Foto: React.FC<{ src: string; inicio: number; dur: number; i: number }> = ({ src, inicio, dur, i }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < inicio - 0.5 || t > inicio + dur + 0.5) return null;
  const a = i === 0 ? 1 : entrada(frame, inicio - 0.3, fps, 0.6);
  const p = interpolate(t, [inicio - 0.3, inicio + dur + 0.3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const lado = i % 2 ? 1 : -1;
  return (
    <AbsoluteFill style={{ opacity: a, overflow: "hidden" }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.04 + p * 0.09}) translateX(${lado * (p - 0.5) * 3}%)` }} />
      {/* barrido de luz que acompaña al encuadre */}
      <AbsoluteFill style={{ background: `linear-gradient(${100 + lado * 12}deg, transparent ${p * 40 - 10}%, rgba(255,235,205,0.07) ${p * 40 + 18}%, transparent ${p * 40 + 50}%)` }} />
    </AbsoluteFill>
  );
};

export const Parallaxe: React.FC<ParallaxeProps> = ({ fotos, capas, titulo, segundosPorFoto, musica }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const { u } = medida(width, height);
  const fin = durationInFrames / fps;
  const a = entrada(frame, 0.6, fps, 0.8);
  const s = salida(frame, fin - 0.2, fps, 0.5);
  return (
    <AbsoluteFill style={{ background: tema.datos.fondo }}>
      {musica ? <Audio src={staticFile(musica)} volume={(f) => interpolate(f, [durationInFrames - 15, durationInFrames], [0.8, 0], { extrapolateLeft: "clamp" })} /> : null}
      {fotos.length ? fotos.map((f, i) => <Foto key={f} src={f} inicio={i * segundosPorFoto} dur={segundosPorFoto} i={i} />) : <Capas capas={capas} total={durationInFrames} />}
      {titulo ? (
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 90 * u }}>
          <div style={{ opacity: a * s, transform: `translateY(${(1 - a) * 26}px)`, color: "#FFFFFF", fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 86 * u, textAlign: "center", lineHeight: 1.08, textShadow: `0 ${4 * u}px ${30 * u}px rgba(0,0,0,0.55)` }}>{titulo}</div>
        </AbsoluteFill>
      ) : null}
      <Acabado />
    </AbsoluteFill>
  );
};
