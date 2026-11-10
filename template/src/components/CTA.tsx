import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, type Palette } from "../theme";

// Botón de llamada a la acción: entrada con rebote y luego respiración (idle motion).
export const CTA: React.FC<{ label: string; palette: Palette; size: number; delay?: number }> = ({
  label,
  palette,
  size,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.bouncy });
  const breathe = 1 + Math.sin(((frame - delay) / fps) * Math.PI * 1.5) * 0.025 * p;

  return (
    <div
      style={{
        fontFamily: theme.fonts.body,
        fontWeight: 600,
        fontSize: size,
        color: palette.bg,
        background: `linear-gradient(135deg, ${palette.accent}, ${palette.accent2})`,
        padding: `${size * 0.6}px ${size * 1.4}px`,
        borderRadius: size * 2,
        opacity: p,
        transform: `translateY(${(1 - p) * 60}px) scale(${(0.7 + p * 0.3) * breathe})`,
        boxShadow: `0 ${size * 0.4}px ${size * 1.6}px ${palette.accent}66`,
      }}
    >
      {label}
    </div>
  );
};
