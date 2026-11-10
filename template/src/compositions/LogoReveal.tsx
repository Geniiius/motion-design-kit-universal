import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { z } from "zod";
import { palettes, paletteNames, theme } from "../theme";
import { Background } from "../components/Background";
import { Grain } from "../components/Grain";
import { useLayout } from "../components/layout";

// Intro / outro de marca: destello de rayos + revelado del logo + eslogan.
export const logoSchema = z.object({
  palette: z.enum(paletteNames),
  brand: z.string(),
  logo: z.string().describe("Ruta en /public (PNG/SVG transparente) o vacío = texto"),
  tagline: z.string(),
  music: z.string(),
});
export type LogoProps = z.infer<typeof logoSchema>;

export const logoDefaults: LogoProps = {
  palette: "ocean",
  brand: "NOVA",
  logo: "",
  tagline: "El futuro del trabajo, hoy.",
  music: "",
};

const RAYS = 12;

export const LogoReveal: React.FC<LogoProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const L = useLayout();
  const pal = palettes[p.palette];

  const ring = spring({ frame, fps, config: theme.spring.smooth });
  const mark = spring({ frame: frame - 12, fps, config: theme.spring.bouncy });
  const tag = spring({ frame: frame - 30, fps, config: theme.spring.smooth });
  const idle = Math.sin((frame / fps) * Math.PI) * 0.015;
  const out = interpolate(frame, [durationInFrames - theme.timing.exit, durationInFrames], [0, 1], {
    easing: theme.easing.in,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ringSize = L.title * 4;

  return (
    <AbsoluteFill style={{ backgroundColor: pal.bg }}>
      <Background palette={pal} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: 1 - out, transform: `scale(${1 + out * 0.1})` }}>
        {/* Rayos en stagger */}
        {Array.from({ length: RAYS }).map((_, i) => {
          const r = spring({ frame: frame - i * 2, fps, config: theme.spring.snappy });
          const fadeRay = interpolate(frame, [25, 50], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                width: 4,
                height: ringSize * 0.9 * r,
                background: `linear-gradient(to top, transparent, ${i % 2 ? pal.accent : pal.accent2})`,
                transform: `rotate(${(360 / RAYS) * i}deg) translateY(-${ringSize * 0.45}px)`,
                transformOrigin: "center bottom",
                opacity: fadeRay,
                bottom: "50%",
              }}
            />
          );
        })}
        <div
          style={{
            position: "absolute",
            width: ringSize,
            height: ringSize,
            borderRadius: "50%",
            border: `3px solid ${pal.accent}`,
            opacity: interpolate(ring, [0, 1], [0, 0.6]),
            transform: `scale(${0.3 + ring * 0.7 + idle})`,
            boxShadow: `0 0 ${ringSize * 0.2}px ${pal.accent}55, inset 0 0 ${ringSize * 0.15}px ${pal.accent2}33`,
          }}
        />
        <div style={{ opacity: mark, transform: `scale(${(0.5 + mark * 0.5) * (1 + idle)})`, filter: `blur(${(1 - mark) * 10}px)` }}>
          {p.logo ? (
            <Img src={staticFile(p.logo)} style={{ height: L.title * 1.6 }} />
          ) : (
            <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: L.title * 1.3, color: pal.text, letterSpacing: "-0.04em" }}>
              {p.brand}
            </div>
          )}
        </div>
        <div
          style={{
            position: "absolute",
            top: `calc(50% + ${ringSize * 0.6}px)`,
            fontFamily: theme.fonts.body,
            fontSize: L.subtitle,
            color: pal.muted,
            opacity: tag,
            transform: `translateY(${(1 - tag) * 30}px)`,
            textAlign: "center",
            padding: `0 ${L.padX}px`,
          }}
        >
          {p.tagline}
        </div>
      </AbsoluteFill>
      <Grain />
      {p.music ? <Audio src={staticFile(p.music)} /> : null}
    </AbsoluteFill>
  );
};
