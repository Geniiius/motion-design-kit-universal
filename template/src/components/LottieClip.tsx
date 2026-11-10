import React, { useEffect, useState } from "react";
import { cancelRender, continueRender, delayRender, staticFile } from "remotion";
import { Lottie, type LottieAnimationData } from "@remotion/lottie";

// Reproduce un archivo Lottie (.json exportado desde After Effects/Bodymovin, LottieFiles…)
// sincronizado con la timeline de Remotion (usa lottie-web por debajo).
// `src` = ruta dentro de /public (ej.: lottie/pulse.json) o URL.
export const LottieClip: React.FC<{ src: string; size: number; loop?: boolean; playbackRate?: number }> = ({
  src,
  size,
  loop = true,
  playbackRate = 1,
}) => {
  const [handle] = useState(() => delayRender(`Cargando Lottie ${src}`));
  const [data, setData] = useState<LottieAnimationData | null>(null);

  useEffect(() => {
    fetch(src.startsWith("http") ? src : staticFile(src))
      .then((r) => r.json())
      .then((json) => {
        setData(json);
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  }, [handle, src]);

  if (!data) return null;
  return <Lottie animationData={data} loop={loop} playbackRate={playbackRate} style={{ width: size, height: size }} />;
};
