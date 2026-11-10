import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { anticipate, backOut, interpolate as mInterpolate, spring as mSpring } from "motion";
import { theme, type Palette } from "../theme";

// Usa las funciones puras de Motion (motion.dev): springs físicos, interpolate
// con varios keyframes y easings (backOut, anticipate). Calculados a partir del tiempo del frame
// -> deterministas. (Los componentes <motion.div> animan en tiempo real: evitarlos en vídeo.)
const springAt = (ms: number, stiffness = 220, damping = 16) =>
  ms <= 0 ? 0 : (mSpring({ keyframes: [0, 1], stiffness, damping }).next(ms).value as number);

export const MotionStats: React.FC<{
  stats: { value: number; suffix: string; label: string }[];
  palette: Palette;
  size: number;
  delay?: number;
}> = ({ stats, palette, size, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = ((frame - delay) / fps) * 1000;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: size * 0.5 }}>
      {stats.map((s, i) => {
        const local = ms - i * 140;
        const pop = springAt(local);
        // Contador: subida rápida con easing backOut
        const count = mInterpolate([0, 1200], [0, s.value], { ease: backOut, clamp: true })(Math.max(0, local));
        // Barra: ligero retroceso y luego impulso (anticipate)
        const bar = mInterpolate([200, 1100], [0, 1], { ease: anticipate, clamp: true })(local);
        return (
          <div
            key={i}
            style={{
              minWidth: size * 4.2,
              padding: `${size * 0.45}px ${size * 0.6}px`,
              borderRadius: size * 0.5,
              background: `${palette.bg2}cc`,
              border: `2px solid ${palette.accent}55`,
              opacity: Math.min(1, pop),
              transform: `translateY(${(1 - pop) * size}px) scale(${0.8 + pop * 0.2})`,
              display: "flex",
              flexDirection: "column",
              gap: size * 0.15,
            }}
          >
            <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: size * 1.3, color: palette.text }}>
              {Math.round(count)}
              <span style={{ color: palette.accent2 }}>{s.suffix}</span>
            </div>
            <div style={{ height: size * 0.12, borderRadius: size, background: `${palette.muted}33`, overflow: "hidden" }}>
              <div style={{ height: "100%", width: `${bar * 100}%`, background: palette.accent }} />
            </div>
            <div style={{ fontFamily: theme.fonts.body, fontSize: size * 0.45, color: palette.muted }}>{s.label}</div>
          </div>
        );
      })}
    </div>
  );
};
