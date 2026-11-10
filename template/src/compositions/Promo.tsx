import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { CalculateMetadataFunction } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { z } from "zod";
import { palettes, paletteNames, theme } from "../theme";
import { Background } from "../components/Background";
import { Grain } from "../components/Grain";
import { KineticText } from "../components/KineticText";
import { Media } from "../components/Media";
import { CTA } from "../components/CTA";
import { useLayout } from "../components/layout";

// ---------- Props editables (Remotion Studio > panel derecho) ----------
export const promoSchema = z.object({
  palette: z.enum(paletteNames),
  brand: z.string(),
  logo: z.string().describe("Ruta en /public (ej.: images/logo.png) o vacío"),
  hook: z.object({ title: z.string(), highlight: z.string() }),
  scenes: z.array(
    z.object({
      title: z.string(),
      highlight: z.string(),
      subtitle: z.string(),
      media: z.string().describe("Imagen/vídeo en /public o URL, vacío = fondo animado"),
    }),
  ),
  cta: z.object({ label: z.string(), url: z.string() }),
  music: z.string().describe("Archivo en /public (ej.: audio/musica/pista.mp3), vacío = sin sonido"),
  sceneSeconds: z.number().min(1.5).max(8),
});
export type PromoProps = z.infer<typeof promoSchema>;

export const promoDefaults: PromoProps = {
  palette: "midnight",
  brand: "NOVA",
  logo: "",
  hook: { title: "Deja de perder tiempo", highlight: "tiempo" },
  scenes: [
    { title: "Todo tu trabajo en un solo lugar", highlight: "solo lugar", subtitle: "Tareas, documentos y equipo sincronizados", media: "" },
    { title: "Automatiza lo repetitivo", highlight: "Automatiza", subtitle: "Gana 5 h por semana, sin esfuerzo", media: "" },
    { title: "Pensado para ir rápido", highlight: "rápido", subtitle: "Lo dominas en 2 minutos", media: "" },
  ],
  cta: { label: "Pruébalo gratis", url: "nova.app" },
  music: "",
  sceneSeconds: 3,
};

const HOOK_S = 2.5;
const END_S = 3.5;
const TRANSITION = theme.timing.transition;

export const calculatePromoMetadata: CalculateMetadataFunction<PromoProps> = ({ props }) => {
  const fps = 30;
  const seqs = [HOOK_S, ...props.scenes.map(() => props.sceneSeconds), END_S].map((s) => Math.round(s * fps));
  const total = seqs.reduce((a, b) => a + b, 0) - TRANSITION * (seqs.length - 1);
  return { durationInFrames: total, fps };
};

// ---------- Escenas ----------
const Hook: React.FC<PromoProps> = (p) => {
  const L = useLayout();
  const pal = palettes[p.palette];
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: L.padX }}>
      <KineticText text={p.hook.title} highlight={p.hook.highlight} size={L.title * 1.15} color={pal.text} highlightColor={pal.accent2} />
    </AbsoluteFill>
  );
};

const Feature: React.FC<{ scene: PromoProps["scenes"][number]; index: number; props: PromoProps }> = ({ scene, index, props }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const pal = palettes[props.palette];
  const sub = spring({ frame: frame - 12, fps, config: theme.spring.smooth });
  const bar = interpolate(frame, [6, 30], [0, 1], { easing: theme.easing.out, extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const vertical = L.format === "vertical" || L.format === "portrait";

  return (
    <AbsoluteFill>
      {scene.media ? <Media src={scene.media} dim={0.5} /> : null}
      <AbsoluteFill
        style={{
          padding: `${L.padTop}px ${L.padX}px ${L.padBottom}px`,
          justifyContent: vertical ? "flex-end" : "center",
          alignItems: "flex-start",
          gap: L.subtitle * 0.8,
        }}
      >
        <div style={{ fontFamily: theme.fonts.body, fontSize: L.small, color: pal.accent2, fontWeight: 600, letterSpacing: "0.2em", opacity: bar }}>
          {String(index + 1).padStart(2, "0")} — {props.brand}
        </div>
        <div style={{ height: 6, width: L.title * 2 * bar, background: pal.accent, borderRadius: 3 }} />
        <KineticText text={scene.title} highlight={scene.highlight} size={L.title} color={pal.text} highlightColor={pal.accent2} align="left" delay={4} />
        <div
          style={{
            fontFamily: theme.fonts.body,
            fontSize: L.subtitle,
            color: pal.muted,
            opacity: sub,
            transform: `translateY(${(1 - sub) * 30}px)`,
          }}
        >
          {scene.subtitle}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const EndCard: React.FC<PromoProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const pal = palettes[p.palette];
  const logo = spring({ frame, fps, config: theme.spring.bouncy });
  const url = spring({ frame: frame - 22, fps, config: theme.spring.smooth });

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: L.subtitle * 1.2, padding: L.padX }}>
      <div style={{ opacity: logo, transform: `scale(${0.6 + logo * 0.4}) rotate(${(1 - logo) * -8}deg)` }}>
        {p.logo ? (
          <Img src={staticFile(p.logo)} style={{ height: L.title * 1.4 }} />
        ) : (
          <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: L.title * 1.2, color: pal.text, letterSpacing: "-0.04em" }}>
            {p.brand}
          </div>
        )}
      </div>
      <CTA label={p.cta.label} palette={pal} size={L.subtitle} delay={10} />
      <div style={{ fontFamily: theme.fonts.body, fontSize: L.small, color: pal.muted, opacity: url, transform: `translateY(${(1 - url) * 20}px)` }}>
        {p.cta.url}
      </div>
    </AbsoluteFill>
  );
};

// ---------- Composición ----------
export const Promo: React.FC<PromoProps> = (props) => {
  const { fps, durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  const pal = palettes[props.palette];
  const timing = springTiming({ config: theme.spring.smooth, durationInFrames: TRANSITION });
  const sceneFrames = Math.round(props.sceneSeconds * fps);
  const musicVolume = interpolate(frame, [0, 15, durationInFrames - 30, durationInFrames], [0, 0.8, 0.8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: pal.bg }}>
      <Background palette={pal} />
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={Math.round(HOOK_S * fps)}>
          <Hook {...props} />
        </TransitionSeries.Sequence>
        {props.scenes.map((scene, i) => (
          <React.Fragment key={i}>
            <TransitionSeries.Transition presentation={slide({ direction: i % 2 ? "from-right" : "from-bottom" })} timing={timing} />
            <TransitionSeries.Sequence durationInFrames={sceneFrames}>
              <Feature scene={scene} index={i} props={props} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        ))}
        <TransitionSeries.Transition presentation={fade()} timing={timing} />
        <TransitionSeries.Sequence durationInFrames={Math.round(END_S * fps)}>
          <EndCard {...props} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Grain />
      {props.music ? <Audio src={staticFile(props.music)} volume={musicVolume} /> : null}
    </AbsoluteFill>
  );
};
