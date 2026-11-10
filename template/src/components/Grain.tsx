import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";

// Capa 5: grano animado + viñeta — elimina el aspecto "plano" generado.
export const Grain: React.FC<{ opacity?: number; vineta?: number }> = ({ opacity = 0.09, vineta = 0.45 }) => {
  const frame = useCurrentFrame();
  const seed = Math.floor(frame / 2) % 50;
  return (
    <>
      <AbsoluteFill style={{ opacity, mixBlendMode: "overlay", pointerEvents: "none" }}>
        <svg width="100%" height="100%">
          <filter id={`grain-${seed}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={3} seed={seed} stitchTiles="stitch" />
          </filter>
          <rect width="100%" height="100%" filter={`url(#grain-${seed})`} />
        </svg>
      </AbsoluteFill>
      <AbsoluteFill
        style={{ background: `radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,${vineta}) 100%)`, pointerEvents: "none" }}
      />
    </>
  );
};
