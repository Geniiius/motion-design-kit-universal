import React from "react";
import { useGsapTimeline } from "../lib/gsap";
import { theme, type Palette } from "../theme";

// Título letra a letra animado con GSAP (stagger, rotación, subrayado) — seek por frame.
export const GsapTitle: React.FC<{ text: string; size: number; palette: Palette; exitAt?: number }> = ({
  text,
  size,
  palette,
  exitAt,
}) => {
  const scope = useGsapTimeline((tl) => {
    tl.from(".char", { yPercent: 130, rotate: 14, opacity: 0, duration: 0.9, ease: "expo.out", stagger: 0.035 })
      .from(".underline", { scaleX: 0, transformOrigin: "left center", duration: 0.7, ease: "power4.inOut" }, "-=0.5")
      .to(".char", { color: palette.accent2, duration: 0.25, stagger: { each: 0.02, yoyo: true, repeat: 1 } }, "+=0.2");
    if (exitAt !== undefined) {
      tl.to(".wrap", { yPercent: -40, opacity: 0, duration: 0.35, ease: "power3.in" }, exitAt);
    }
  });

  return (
    <div ref={scope} style={{ display: "flex", justifyContent: "center" }}>
      <div className="wrap" style={{ display: "inline-flex", flexDirection: "column", alignItems: "stretch" }}>
        <div
          style={{
            fontFamily: theme.fonts.display,
            fontWeight: 700,
            fontSize: size,
            color: palette.text,
            letterSpacing: "-0.03em",
            overflow: "hidden",
            lineHeight: 1.1,
            whiteSpace: "pre",
          }}
        >
          {text.split("").map((c, i) => (
            <span key={i} className="char" style={{ display: "inline-block" }}>
              {c}
            </span>
          ))}
        </div>
        <div className="underline" style={{ height: size * 0.08, background: palette.accent, borderRadius: size }} />
      </div>
    </div>
  );
};
