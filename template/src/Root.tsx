import React from "react";
import { Composition, Folder } from "remotion";
import { Promo, promoSchema, promoDefaults, calculatePromoMetadata } from "./compositions/Promo";
import { KineticReel, kineticSchema, kineticDefaults, calculateKineticMetadata } from "./compositions/KineticReel";
import { LogoReveal, logoSchema, logoDefaults } from "./compositions/LogoReveal";
import { StackShowcase, showcaseSchema, showcaseDefaults, SHOWCASE_DURATION } from "./compositions/StackShowcase";
import { CompositionsUniversal } from "./universal/Compositions";

// Formatos estándar de las redes sociales
const FORMATS = {
  Reel: { width: 1080, height: 1920 }, // 9:16 — Reels, TikTok, Shorts, Stories
  Feed: { width: 1080, height: 1350 }, // 4:5  — feed Instagram / Facebook / LinkedIn
  Square: { width: 1080, height: 1080 }, // 1:1 — carruseles, anuncios
  Landscape: { width: 1920, height: 1080 }, // 16:9 — YouTube, web, presentaciones
} as const;

type FormatName = keyof typeof FORMATS;
const ALL = Object.keys(FORMATS) as FormatName[];

export const RemotionRoot: React.FC = () => (
  <>
    <Folder name="Promo">
      {ALL.map((f) => (
        <Composition
          key={f}
          id={`Promo-${f}`}
          component={Promo}
          schema={promoSchema}
          defaultProps={promoDefaults}
          calculateMetadata={calculatePromoMetadata}
          durationInFrames={300}
          fps={30}
          {...FORMATS[f]}
        />
      ))}
    </Folder>
    <Folder name="KineticReel">
      {(["Reel", "Feed", "Square"] as FormatName[]).map((f) => (
        <Composition
          key={f}
          id={`Kinetic-${f}`}
          component={KineticReel}
          schema={kineticSchema}
          defaultProps={kineticDefaults}
          calculateMetadata={calculateKineticMetadata}
          durationInFrames={300}
          fps={30}
          {...FORMATS[f]}
        />
      ))}
    </Folder>
    <Folder name="LogoReveal">
      {ALL.map((f) => (
        <Composition
          key={f}
          id={`Logo-${f}`}
          component={LogoReveal}
          schema={logoSchema}
          defaultProps={logoDefaults}
          durationInFrames={90}
          fps={30}
          {...FORMATS[f]}
        />
      ))}
    </Folder>
    <Folder name="Showcase-GSAP-Motion-Lottie">
      {(["Reel", "Landscape"] as FormatName[]).map((f) => (
        <Composition
          key={f}
          id={`Showcase-${f}`}
          component={StackShowcase}
          schema={showcaseSchema}
          defaultProps={showcaseDefaults}
          durationInFrames={SHOWCASE_DURATION}
          fps={30}
          {...FORMATS[f]}
        />
      ))}
    </Folder>
    <CompositionsUniversal />
  </>
);
