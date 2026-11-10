import React from "react";
import { AbsoluteFill, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { palettes, paletteNames, theme } from "../theme";
import { Background } from "../components/Background";
import { Grain } from "../components/Grain";
import { GsapTitle } from "../components/GsapTitle";
import { MotionStats } from "../components/MotionStats";
import { LottieClip } from "../components/LottieClip";
import { KineticText } from "../components/KineticText";
import { useLayout } from "../components/layout";

// Demo de los 4 motores de animación del kit en un solo vídeo:
// Remotion (timeline) + GSAP (título) + Motion (estadísticas) + lottie-web (icono animado).
export const showcaseSchema = z.object({
  palette: z.enum(paletteNames),
  title: z.string(),
  stats: z.array(z.object({ value: z.number(), suffix: z.string(), label: z.string() })),
  lottie: z.string().describe("Archivo Lottie en /public o URL"),
  closing: z.string(),
});
export type ShowcaseProps = z.infer<typeof showcaseSchema>;

export const showcaseDefaults: ShowcaseProps = {
  palette: "midnight",
  title: "Lanzamiento 2026",
  stats: [
    { value: 250, suffix: "%", label: "de conversiones" },
    { value: 12, suffix: "k", label: "usuarios" },
    { value: 4, suffix: "x", label: "más rápido" },
  ],
  lottie: "lottie/pulse.json",
  closing: "Disponible desde hoy",
};

const S = { title: 75, stats: 105, lottie: 90 }; // frames a 30 fps
export const SHOWCASE_DURATION = S.title + S.stats + S.lottie;

const LottieScene: React.FC<ShowcaseProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const pal = palettes[p.palette];
  const pop = spring({ frame, fps, config: theme.spring.bouncy });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: L.subtitle, padding: L.padX }}>
      <div style={{ opacity: pop, transform: `scale(${0.6 + pop * 0.4})` }}>
        <LottieClip src={p.lottie} size={L.title * 3} />
      </div>
      <KineticText text={p.closing} size={L.title * 0.7} color={pal.text} highlight="hoy" highlightColor={pal.accent2} delay={8} />
    </AbsoluteFill>
  );
};

export const StackShowcase: React.FC<ShowcaseProps> = (p) => {
  const L = useLayout();
  const pal = palettes[p.palette];
  return (
    <AbsoluteFill style={{ backgroundColor: pal.bg }}>
      <Background palette={pal} />
      <Sequence durationInFrames={S.title}>
        <AbsoluteFill style={{ justifyContent: "center", padding: L.padX }}>
          <GsapTitle text={p.title} size={L.title * (L.format === "landscape" ? 1 : 0.85)} palette={pal} exitAt={(S.title - 12) / 30} />
        </AbsoluteFill>
      </Sequence>
      <Sequence from={S.title} durationInFrames={S.stats}>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: L.padX }}>
          <MotionStats stats={p.stats} palette={pal} size={L.subtitle * (L.format === "landscape" ? 1 : 1.5)} delay={4} />
        </AbsoluteFill>
      </Sequence>
      <Sequence from={S.title + S.stats} durationInFrames={S.lottie}>
        <LottieScene {...p} />
      </Sequence>
      <Grain />
    </AbsoluteFill>
  );
};
