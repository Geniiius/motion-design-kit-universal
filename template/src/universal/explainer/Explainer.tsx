import React from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, staticFile } from "remotion";
import { z } from "zod";
import { Acabado, FondoVivo, Subtitulo } from "../capas";
import { tema } from "../tema";
import { Comparison, ConceptReveal, DataChart, FichaFuente, FlowDiagram, StepByStepExplainer, Timeline } from "./piezas";
import demo from "./demo-datos.json";

const palabra = z.object({ text: z.string(), start: z.number(), end: z.number() });
const escena = z.object({
  tipo: z.enum(["concepto", "curva", "comparacion", "flujo", "cronologia", "pasos", "fuente"]),
  inicio: z.number(),
  fin: z.number(),
  rotulo: z.string().default(""),
  titulo: z.string().default(""),
  definicion: z.string().default(""),
  unidad: z.string().default(""),
  pasos: z.array(z.string()).default([]),
  barras: z.array(z.object({ etiqueta: z.string(), valor: z.number() })).default([]),
  hitos: z.array(z.object({ fecha: z.string(), texto: z.string() })).default([]),
  lineas: z.array(z.string()).default([]),
  inicioDibujo: z.number().optional(),
  finDibujo: z.number().optional(),
});

export const explainerSchema = z.object({
  duracion: z.number(),
  coma: z.boolean().describe("Coma decimal (francés, español)").optional(),
  voz: z.string().describe("Archivo en /public o vacío"),
  words: z.array(palabra),
  serie: z.array(z.object({ x: z.number(), y: z.number() })),
  escenas: z.array(escena),
});
export type ExplainerProps = z.infer<typeof explainerSchema>;
export const explainerDefaults = demo as unknown as ExplainerProps;

export const calculateExplainer: CalculateMetadataFunction<ExplainerProps> = ({ props }) => ({ durationInFrames: Math.ceil(props.duracion * 30), fps: 30 });

export const Explainer: React.FC<ExplainerProps> = ({ voz, words, serie, escenas, coma = false }) => (
  <AbsoluteFill>
    <FondoVivo a={tema.datos.fondo} b={tema.datos.fondo2} c="#10344A" />
    {voz ? <Audio src={staticFile(voz)} /> : null}
    {escenas.map((e, i) => {
      const v = { inicio: e.inicio, fin: e.fin };
      if (e.tipo === "concepto") return <ConceptReveal key={i} {...v} rotulo={e.rotulo} titulo={e.titulo} definicion={e.definicion} />;
      if (e.tipo === "curva") return <DataChart key={i} {...v} serie={serie} unidad={e.unidad} rotulo={e.rotulo} inicioDibujo={e.inicioDibujo} finDibujo={e.finDibujo} decimales={2} coma={coma} />;
      if (e.tipo === "comparacion") return <Comparison key={i} {...v} rotulo={e.rotulo} unidad={e.unidad} barras={e.barras} coma={coma} />;
      if (e.tipo === "flujo") return <FlowDiagram key={i} {...v} rotulo={e.rotulo} pasos={e.pasos} />;
      if (e.tipo === "cronologia") return <Timeline key={i} {...v} rotulo={e.rotulo} hitos={e.hitos} />;
      if (e.tipo === "pasos") return <StepByStepExplainer key={i} {...v} rotulo={e.rotulo} pasos={e.pasos} />;
      return <FichaFuente key={i} {...v} rotulo={e.rotulo} lineas={e.lineas} />;
    })}
    <Subtitulo words={words} />
    <Acabado />
  </AbsoluteFill>
);
