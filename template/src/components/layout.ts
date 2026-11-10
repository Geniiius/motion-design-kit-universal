import { useVideoConfig } from "remotion";

export type Format = "vertical" | "portrait" | "square" | "landscape";

// Adapta tamaños y márgenes al formato (9:16, 4:5, 1:1, 16:9). Respeta las zonas seguras de Reels/TikTok.
export const useLayout = () => {
  const { width, height } = useVideoConfig();
  const ratio = width / height;
  const format: Format = ratio < 0.7 ? "vertical" : ratio < 0.95 ? "portrait" : ratio < 1.2 ? "square" : "landscape";
  const base = Math.min(width, height);
  return {
    format,
    title: base * (format === "landscape" ? 0.1 : 0.115),
    subtitle: base * 0.045,
    small: base * 0.032,
    // Reels/TikTok: ~14 % arriba y ~20 % abajo quedan tapados por la interfaz
    padTop: format === "vertical" ? height * 0.14 : height * 0.08,
    padBottom: format === "vertical" ? height * 0.2 : height * 0.08,
    padX: width * 0.08,
  };
};
