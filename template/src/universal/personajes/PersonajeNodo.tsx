import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, staticFile, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { z } from "zod";
import { Acabado, Subtitulo } from "../capas";
import { Camara, Entorno, SetEstudio, Toma, useTiempo } from "../escena/Estudio3D";
import { medida, tema } from "../tema";
import { bocaEn, Gesto, poseEn } from "./gestos";
import { Nodo } from "./Nodo";

const gesto = z.object({ tipo: z.enum(["saludar", "senalar", "asentir", "reaccionar", "contar", "saltar"]), inicio: z.number(), fin: z.number(), lado: z.union([z.literal(1), z.literal(-1)]).optional() });

export const personajeSchema = z.object({
  duracion: z.number(),
  voz: z.string().describe("Archivo en /public o vacío"),
  words: z.array(z.object({ text: z.string(), start: z.number(), end: z.number() })),
  visemas: z.array(z.object({ id: z.number(), start: z.number(), duration: z.number() })),
  envolvente: z.array(z.number()),
  gestos: z.array(gesto),
  cortes: z.array(z.number()).describe("Segundos donde cambia el plano, sobre la primera palabra de cada idea"),
});
export type PersonajeProps = z.infer<typeof personajeSchema>;

export const personajeDefaults: PersonajeProps = {
  duracion: 6,
  voz: "",
  words: [],
  visemas: [],
  envolvente: [],
  gestos: [
    { tipo: "saludar", inicio: 0.4, fin: 2.2, lado: 1 },
    { tipo: "senalar", inicio: 3, fin: 4.6, lado: -1 },
    { tipo: "reaccionar", inicio: 4.8, fin: 5.8 },
  ],
  cortes: [3],
};

export const calculatePersonaje: CalculateMetadataFunction<PersonajeProps> = ({ props }) => ({ durationInFrames: Math.ceil(props.duracion * 30), fps: 30 });

// Plano general -> plano medio en arco -> primer plano: mismo personaje, tres distancias.
const tomasDe = (cortes: number[], duracion: number, vertical: boolean): Toma[] => {
  const k = vertical ? 1.55 : 1;
  const [c1 = duracion * 0.4, c2 = duracion * 0.72] = cortes;
  return [
    { t: 0, pos: [0, 0.6, 11 * k], mira: [0, 0.05, 0], fov: 28 },
    { t: c1 - 0.001, pos: [0.4, 0.5, 9.2 * k], mira: [0, 0.05, 0], fov: 28 },
    { t: c1, pos: [-3.1, 0.75, 6.8 * k], mira: [0.1, 0.25, 0], fov: 28, corte: true },
    { t: c2 - 0.001, pos: [-1.9, 0.6, 6.5 * k], mira: [0.1, 0.25, 0], fov: 28 },
    { t: c2, pos: [0.8, 0.6, 6.4 * k], mira: [0, 0.42, 0], fov: 24, corte: true },
    { t: duracion, pos: [0.3, 0.42, 5.7 * k], mira: [0, 0.42, 0], fov: 24 },
  ];
};

export const PersonajeNodo: React.FC<PersonajeProps> = ({ duracion, voz, words, visemas, envolvente, gestos, cortes }) => {
  const t = useTiempo();
  const { width, height } = useVideoConfig();
  const { vertical } = medida(width, height);
  const amp = envolvente[Math.floor(t * 30)] ?? 0;
  const hablando = words.length ? (words.some((w) => w.start <= t && t <= w.end + 0.06) ? 1 : 0) : 0;
  const pose = poseEn(t, gestos as Gesto[], hablando);
  const boca = bocaEn(t, visemas, envolvente);
  return (
    <AbsoluteFill style={{ background: tema.estudio.fondo }}>
      {voz ? <Audio src={staticFile(voz)} /> : null}
      <ThreeCanvas width={width} height={height} shadows gl={{ antialias: true, preserveDrawingBuffer: true }}>
        <Camara t={t} tomas={tomasDe(cortes, duracion, vertical)} />
        <Entorno />
        <SetEstudio />
        <Nodo pose={pose} boca={boca} energia={amp} />
      </ThreeCanvas>
      <Subtitulo words={words} color={tema.estudio.sub} apagado="rgba(255,255,255,0.45)" fondo={tema.estudio.subFondo} />
      <Acabado vineta={0.07} grano={0.03} />
    </AbsoluteFill>
  );
};
