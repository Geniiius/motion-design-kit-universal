// theme.ts — fuente única de verdad para cada proyecto Remotion.
// NUNCA escribir colores, easings ni springs directamente en los componentes.
import { Easing } from "remotion";

export const theme = {
  colors: {
    // Ajustar a la marca del usuario. Por defecto: tech oscuro.
    bg: "#0A0A0F",
    bgAlt: "#12121A",
    primary: "#7C3AED", // EL color protagonista — máx. un elemento por fotograma
    accent: "#22D3EE",
    text: "#F4F4F5",
    textDim: "#A1A1AA",
    glow: "rgba(124, 58, 237, 0.4)",
  },
  fonts: {
    display: "Clash Display", // cargar con @font-face + staticFile, o google-fonts
    body: "Inter",
    mono: "JetBrains Mono",
  },
  // LAS curvas de easing. Lineal prohibido.
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1), // easeOutExpo — entradas
    inOut: Easing.bezier(0.83, 0, 0.17, 1), // easeInOutQuint — desplazamientos, Ken Burns
    in: Easing.bezier(0.7, 0, 0.84, 0), // solo salidas
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 }, // pops de UI, palabras
    smooth: { damping: 20, stiffness: 90, mass: 1 }, // elementos grandes
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 }, // acentos divertidos, logos
  },
} as const;
