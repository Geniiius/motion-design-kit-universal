import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { Palette } from "../theme";

// Capa 1: degradado animado (nunca un fondo plano).
export const Background: React.FC<{ palette: Palette }> = ({ palette }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const x1 = 30 + Math.sin(t * 0.6) * 15;
  const y1 = 25 + Math.cos(t * 0.5) * 12;
  const x2 = 70 + Math.cos(t * 0.4) * 18;
  const y2 = 75 + Math.sin(t * 0.7) * 10;

  return (
    <AbsoluteFill
      style={{
        background: [
          `radial-gradient(circle at ${x1}% ${y1}%, ${palette.accent}55 0%, transparent 45%)`,
          `radial-gradient(circle at ${x2}% ${y2}%, ${palette.accent2}40 0%, transparent 50%)`,
          `linear-gradient(160deg, ${palette.bg} 0%, ${palette.bg2} 100%)`,
        ].join(","),
      }}
    />
  );
};
