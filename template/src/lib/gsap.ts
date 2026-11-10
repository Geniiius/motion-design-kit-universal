import { useLayoutEffect, useRef } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import gsap from "gsap";

/**
 * GSAP controlado por Remotion: la timeline se construye en pausa y se posiciona ("seek")
 * en frame / fps en cada render. Resultado 100 % determinista (sin ticker ni tiempo real),
 * compatible con el render multihilo de Remotion.
 *
 *   const scope = useGsapTimeline((tl) => {
 *     tl.from(".char", { yPercent: 120, stagger: 0.03, ease: "expo.out", duration: 0.8 });
 *   });
 *   return <div ref={scope}>...</div>;
 */
export const useGsapTimeline = <T extends HTMLElement = HTMLDivElement>(build: (tl: gsap.core.Timeline) => void) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scope = useRef<T>(null);
  const tl = useRef<gsap.core.Timeline | null>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      tl.current = gsap.timeline({ paused: true });
      build(tl.current);
    }, scope);
    return () => ctx.revert();
    // La timeline se construye una sola vez; solo el seek depende del frame.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useLayoutEffect(() => {
    tl.current?.seek(frame / fps, false);
  }, [frame, fps]);

  return scope;
};
