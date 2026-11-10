import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { CalculateMetadataFunction } from "remotion";
import { z } from "zod";
import { palettes, paletteNames, theme } from "../theme";
import { Background } from "../components/Background";
import { Grain } from "../components/Grain";
import { KineticText } from "../components/KineticText";
import { Media } from "../components/Media";
import { useLayout } from "../components/layout";

// Reel de "texto en movimiento": consejos, citas, listas, storytelling, anuncios.
export const kineticSchema = z.object({
  palette: z.enum(paletteNames),
  handle: z.string().describe("@cuenta mostrada abajo"),
  beats: z.array(
    z.object({
      text: z.string(),
      highlight: z.string(),
      seconds: z.number().min(0.8).max(6),
      media: z.string().describe("Imagen/vídeo de fondo opcional"),
    }),
  ),
  music: z.string(),
});
export type KineticProps = z.infer<typeof kineticSchema>;

export const kineticDefaults: KineticProps = {
  palette: "sunset",
  handle: "@tucuenta",
  beats: [
    { text: "3 errores que matan tus Reels", highlight: "matan", seconds: 2.2, media: "" },
    { text: "1. Sin hook en los 2 primeros segundos", highlight: "hook", seconds: 2.4, media: "" },
    { text: "2. Texto ilegible en el móvil", highlight: "ilegible", seconds: 2.2, media: "" },
    { text: "3. Ninguna razón para verlo hasta el final", highlight: "final", seconds: 2.4, media: "" },
    { text: "Guárdalo para tu próximo post", highlight: "Guárdalo", seconds: 2.4, media: "" },
  ],
  music: "",
};

export const calculateKineticMetadata: CalculateMetadataFunction<KineticProps> = ({ props }) => {
  const fps = 30;
  return { fps, durationInFrames: props.beats.reduce((a, b) => a + Math.round(b.seconds * fps), 0) };
};

const Beat: React.FC<{ beat: KineticProps["beats"][number]; props: KineticProps; dur: number; index: number }> = ({
  beat,
  props,
  dur,
  index,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const L = useLayout();
  const pal = palettes[props.palette];
  // Destello de acento en cada cambio de bloque = ritmo visual
  const flash = interpolate(frame, [0, 8], [0.35, 0], { easing: theme.easing.out, extrapolateRight: "clamp" });
  const punch = spring({ frame, fps, config: theme.spring.snappy });
  const tilt = index % 2 ? -1.5 : 1.5;

  return (
    <AbsoluteFill>
      {beat.media ? <Media src={beat.media} dim={0.55} /> : null}
      <AbsoluteFill style={{ backgroundColor: pal.accent, opacity: flash }} />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: `${L.padTop}px ${L.padX}px ${L.padBottom}px`,
          transform: `rotate(${(1 - punch) * tilt}deg) scale(${0.96 + punch * 0.04})`,
        }}
      >
        <KineticText
          text={beat.text}
          highlight={beat.highlight}
          size={L.title * (beat.text.length > 40 ? 0.85 : 1.05)}
          color={pal.text}
          highlightColor={pal.accent2}
          exitAt={dur - theme.timing.exit}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Progress: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, height } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        height: Math.max(6, height * 0.005),
        width: `${(frame / durationInFrames) * 100}%`,
        background: color,
      }}
    />
  );
};

export const KineticReel: React.FC<KineticProps> = (props) => {
  const { fps, durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  const L = useLayout();
  const pal = palettes[props.palette];
  let from = 0;
  const handleIn = spring({ frame: frame - 10, fps, config: theme.spring.smooth });
  const musicVolume = interpolate(frame, [0, 10, durationInFrames - 20, durationInFrames], [0, 0.8, 0.8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: pal.bg }}>
      <Background palette={pal} />
      {props.beats.map((beat, i) => {
        const dur = Math.round(beat.seconds * fps);
        const seq = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <Beat beat={beat} props={props} dur={dur} index={i} />
          </Sequence>
        );
        from += dur;
        return seq;
      })}
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: L.padBottom * 0.6 }}>
        <div style={{ fontFamily: theme.fonts.body, fontWeight: 600, fontSize: L.small, color: pal.muted, opacity: handleIn }}>
          {props.handle}
        </div>
      </AbsoluteFill>
      <Progress color={pal.accent2} />
      <Grain />
      {props.music ? <Audio src={staticFile(props.music)} volume={musicVolume} /> : null}
    </AbsoluteFill>
  );
};
