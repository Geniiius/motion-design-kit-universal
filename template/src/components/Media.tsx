import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const resolve = (src: string) => (src.startsWith("http") ? src : staticFile(src));

// Capa 2: imagen (Ken Burns) o vídeo (OffthreadVideo). `src` = ruta dentro de /public o URL.
export const Media: React.FC<{ src: string; dim?: number }> = ({ src, dim = 0.35 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const isVideo = /\.(mp4|webm|mov)$/i.test(src);
  const scale = interpolate(frame, [0, durationInFrames], [1, 1.08], { extrapolateRight: "clamp" });
  const pan = interpolate(frame, [0, durationInFrames], [0, -2], { extrapolateRight: "clamp" });
  const style: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover" };

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: isVideo ? undefined : `scale(${scale}) translateX(${pan}%)` }}>
        {isVideo ? <OffthreadVideo src={resolve(src)} muted style={style} /> : <Img src={resolve(src)} style={style} />}
      </AbsoluteFill>
      <AbsoluteFill style={{ background: `rgba(0,0,0,${dim})` }} />
    </AbsoluteFill>
  );
};
