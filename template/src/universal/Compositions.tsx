import React from "react";
import { Composition, Folder } from "remotion";
import { Escena3D, escenaDefaults, escenaSchema, Hibrido, hibridoDefaults, hibridoSchema } from "./escena/Escena3D";
import { calculateParallaxe, Parallaxe, parallaxeDefaults, parallaxeSchema } from "./escena/Parallaxe";
import { calculateExplainer, Explainer, explainerDefaults, explainerSchema } from "./explainer/Explainer";
import { calculateGlb, glbDefaults, glbSchema, PersonajeGLB } from "./personajes/ModeloGLB";
import { calculatePersonaje, personajeDefaults, personajeSchema, PersonajeNodo } from "./personajes/PersonajeNodo";

const FORMATS = {
  Landscape: { width: 1920, height: 1080 },
  Reel: { width: 1080, height: 1920 },
  Square: { width: 1080, height: 1080 },
  Feed: { width: 1080, height: 1350 },
} as const;
type Formato = keyof typeof FORMATS;
const TODOS = Object.keys(FORMATS) as Formato[];

export const CompositionsUniversal: React.FC = () => (
  <Folder name="Universal">
    {TODOS.map((f) => (
      <React.Fragment key={f}>
        <Composition id={`Explainer-${f}`} component={Explainer} schema={explainerSchema} defaultProps={explainerDefaults} calculateMetadata={calculateExplainer} durationInFrames={300} fps={30} {...FORMATS[f]} />
        <Composition id={`Personaje-Nodo-${f}`} component={PersonajeNodo} schema={personajeSchema} defaultProps={personajeDefaults} calculateMetadata={calculatePersonaje} durationInFrames={180} fps={30} {...FORMATS[f]} />
        <Composition id={`Personaje-GLB-${f}`} component={PersonajeGLB} schema={glbSchema} defaultProps={glbDefaults} calculateMetadata={calculateGlb} durationInFrames={180} fps={30} {...FORMATS[f]} />
        <Composition id={`Parallaxe-${f}`} component={Parallaxe} schema={parallaxeSchema} defaultProps={parallaxeDefaults} calculateMetadata={calculateParallaxe} durationInFrames={240} fps={30} {...FORMATS[f]} />
        <Composition id={`Escena3D-${f}`} component={Escena3D} schema={escenaSchema} defaultProps={escenaDefaults} durationInFrames={240} fps={30} {...FORMATS[f]} />
        <Composition id={`Hibrido-${f}`} component={Hibrido} schema={hibridoSchema} defaultProps={hibridoDefaults} durationInFrames={180} fps={30} {...FORMATS[f]} />
      </React.Fragment>
    ))}
  </Folder>
);
