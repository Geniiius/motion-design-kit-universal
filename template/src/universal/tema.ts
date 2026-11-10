import { theme } from "../theme";

// Tema único de las composiciones Universal: ningún color ni easing se escribe en otro sitio.
export const tema = {
  fuentes: theme.fonts,
  easing: theme.easing,
  spring: theme.spring,
  datos: { fondo: "#0B1020", fondo2: "#17224A", tinta: "#F2F4FA", suave: "#A9B4CE", acento: "#5CE1C6", acento2: "#FFB454", linea: "#2C3860", panel: "rgba(23,34,74,0.72)" },
  estudio: { fondo: "#DCE4F2", suelo: "#E6ECF6", arco: "#C3CFE6", tinta: "#101A33", sub: "#FFFFFF", subFondo: "rgba(16,26,51,0.82)" },
  cine: { fondo: "#05070C", metal: "#AEB7C6", oscuro: "#11151D", brillo: "#FFC98A", frio: "#6FB7FF", tinta: "#F4EFE6" },
} as const;

// Escala relativa al lado corto: la misma composición sirve para 16:9, 9:16, 1:1 y 4:5.
export const medida = (width: number, height: number) => ({ u: Math.min(width, height) / 1080, vertical: height > width });

export const palabrasDe = (words: { text: string; start: number; end: number }[], t: number, antes = 0.04) => {
  let i = -1;
  for (let k = 0; k < words.length; k++) if (words[k].start - antes <= t) i = k;
  return i;
};
