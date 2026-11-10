import { Easing } from "remotion";
import { fuentes } from "./fuentes";

// Tema único: ningún color / easing / spring debe escribirse directamente en otro sitio.
export const theme = {
  fonts: {
    display: fuentes.display,
    body: fuentes.body,
  },
  easing: {
    out: Easing.bezier(0.16, 1, 0.3, 1), // expo out: entradas
    in: Easing.bezier(0.7, 0, 0.84, 0), // expo in: salidas
    inOut: Easing.bezier(0.65, 0, 0.35, 1),
  },
  spring: {
    snappy: { damping: 14, stiffness: 180, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 9, stiffness: 140, mass: 0.7 },
  },
  timing: {
    stagger: 4, // frames entre dos elementos
    exit: 10, // frames de salida (más corta que la entrada)
    transition: 15,
  },
} as const;

// Paletas listas para usar — se eligen con la prop `palette`.
export const palettes = {
  midnight: { bg: "#0B0D17", bg2: "#1B1F3B", accent: "#7C5CFF", accent2: "#00E0B8", text: "#F5F6FA", muted: "#9BA1C0" },
  sunset: { bg: "#1A0B12", bg2: "#3D1426", accent: "#FF5E3A", accent2: "#FFC542", text: "#FFF6EE", muted: "#D7A9A0" },
  ocean: { bg: "#03141F", bg2: "#08324A", accent: "#00B4FF", accent2: "#7CFFCB", text: "#F0FAFF", muted: "#8FB7CC" },
  mono: { bg: "#0A0A0A", bg2: "#1F1F1F", accent: "#FFFFFF", accent2: "#C8FF00", text: "#FFFFFF", muted: "#8A8A8A" },
  cream: { bg: "#F4EFE6", bg2: "#E5DBC8", accent: "#E8462C", accent2: "#1F3A5F", text: "#1A1A1A", muted: "#6B6357" },
} as const;

export type PaletteName = keyof typeof palettes;
export type Palette = (typeof palettes)[PaletteName];
export const paletteNames = Object.keys(palettes) as [PaletteName, ...PaletteName[]];
