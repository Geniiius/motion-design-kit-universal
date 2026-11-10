import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

type Props = {
  text: string;
  size: number;
  color: string;
  highlight?: string; // palabra(s) en color de acento
  highlightColor?: string;
  delay?: number;
  exitAt?: number; // frame local donde empieza la salida
  weight?: number;
  align?: "left" | "center";
  font?: string;
};

const clean = (w: string) => w.toLowerCase().replace(/[^\p{L}\p{N}]/gu, "");

// Entrada palabra a palabra: opacidad + translateY + escala + blur, en stagger.
export const KineticText: React.FC<Props> = ({
  text,
  size,
  color,
  highlight,
  highlightColor,
  delay = 0,
  exitAt,
  weight = 700,
  align = "center",
  font = theme.fonts.display,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");
  const hl = (highlight ?? "").split(" ").map(clean).filter(Boolean);

  const exit =
    exitAt === undefined
      ? 0
      : interpolate(frame, [exitAt, exitAt + theme.timing.exit], [0, 1], {
          easing: theme.easing.in,
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  return (
    <div
      style={{
        fontFamily: font,
        fontSize: size,
        fontWeight: weight,
        color,
        lineHeight: 1.05,
        letterSpacing: "-0.03em",
        textAlign: align,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: align === "center" ? "center" : "flex-start",
        gap: `0 ${size * 0.25}px`,
        opacity: 1 - exit,
        transform: `translateY(${-exit * size * 0.4}px)`,
      }}
    >
      {words.map((w, i) => {
        const p = spring({ frame: frame - delay - i * theme.timing.stagger, fps, config: theme.spring.snappy });
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: p,
              transform: `translateY(${(1 - p) * size * 0.6}px) scale(${0.85 + p * 0.15})`,
              filter: `blur(${(1 - p) * 8}px)`,
              color: hl.includes(clean(w)) ? highlightColor : color,
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};
