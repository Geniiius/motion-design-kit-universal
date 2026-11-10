# Patrones de movimiento — biblioteca de componentes

Implementaciones probadas. Importar `theme` desde `src/theme.ts` del proyecto.
Todos los componentes usan `useCurrentFrame()` / `useVideoConfig()` de remotion.

## Contenido
1. Entrada premium (la más usada)
2. Hijos en stagger
3. Revelado de texto palabra a palabra
4. Fondo degradado animado (nunca fondos planos)
5. Capa de etalonaje
6. Grano procedural (sin archivos)
7. Viñeta
8. Ken Burns para imágenes fijas
9. Contador animado
10. Destello / logo radial
11. Salidas
12. Respiración en reposo
13. Profundidad con parallax
14. Transiciones (librería + a mano)
15. Motion blur
16. Sincronización de audio y efectos
17. Subtítulos sincronizados con la voz

---

## 1. Entrada premium (fundido + subida + escala)
```tsx
const Entrance: React.FC<{delay?: number; children: React.ReactNode}> =
({ delay = 0, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.smooth });
  return (
    <div style={{
      opacity: p,
      transform: `translateY(${interpolate(p, [0, 1], [40, 0])}px)
                  scale(${interpolate(p, [0, 1], [0.94, 1])})`,
    }}>{children}</div>
  );
};
```
Con bezier en vez de spring (deslizamientos controlados):
```tsx
const x = interpolate(frame, [0, 25], [60, 0], {
  easing: theme.ease.out,
  extrapolateLeft: "clamp", extrapolateRight: "clamp", // SIEMPRE los dos
});
```

## 2. Hijos en stagger
```tsx
{items.map((item, i) => <Entrance key={i} delay={start + i * 4}>{item}</Entrance>)}
```
Desfases de 3–6 frames. Palabras: 3. Tarjetas/listas: 4–5. Bloques grandes: 6.

## 3. Revelado palabra a palabra
```tsx
const WordReveal: React.FC<{text: string; delay?: number; per?: number;
  style?: React.CSSProperties}> = ({ text, delay = 0, per = 3, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.26em", ...style }}>
      {text.split(" ").map((word, i) => {
        const p = spring({ frame: frame - delay - i * per, fps,
          config: theme.spring.snappy });
        return (
          <span key={i} style={{
            display: "inline-block", opacity: p,
            transform: `translateY(${interpolate(p, [0, 1], [30, 0])}px)`,
          }}>{word}</span>
        );
      })}
    </div>
  );
};
```
OJO: al poner dos bloques de texto grandes lado a lado en una fila flex, usar un `gap` en
píxeles (p. ej. `gap: 42`), NO en em: em se calcula con la fuente del padre (normalmente
16 px) y da espacios casi nulos junto a tipografía de 150 px.

## 4. Fondo degradado animado
```tsx
const BgMesh: React.FC = () => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 55) * 50, d2 = Math.cos(frame / 70) * 40;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <div style={{ position: "absolute", width: 1200, height: 1200,
        borderRadius: "50%", top: -450, left: -300 + d1, filter: "blur(50px)",
        background: `radial-gradient(circle, ${theme.colors.primary}33, transparent 62%)` }}/>
      <div style={{ position: "absolute", width: 900, height: 900,
        borderRadius: "50%", bottom: -400, right: -250 - d2, filter: "blur(70px)",
        background: `radial-gradient(circle, ${theme.colors.accent}22, transparent 65%)` }}/>
    </AbsoluteFill>
  );
};
```

## 5. Etalonaje (ENCIMA de todo el contenido, debajo del grano)
Unifica assets dispares (imágenes IA + B-roll + capturas) en un mismo look.
```tsx
const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ backgroundColor: theme.colors.primary,
      mixBlendMode: "soft-light", opacity: 0.18 }}/>
    <AbsoluteFill style={{ background:
      "linear-gradient(180deg, rgba(0,0,0,0.10), transparent 28%, transparent 72%, rgba(0,0,0,0.2))" }}/>
  </AbsoluteFill>
);
```
Opacidad 0,10–0,15 en temas claros, 0,18–0,25 en oscuros. Si un clip sigue destacando:
`filter: "saturate(1.1) contrast(1.08)"`.

## 6. Grano procedural — sin archivos
```tsx
const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const noise = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;
  return <AbsoluteFill style={{ pointerEvents: "none",
    backgroundImage: noise, backgroundSize: "220px",
    backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`, // parpadeo de película
    opacity: 0.05, mixBlendMode: "multiply" }}/>; // "overlay" en temas oscuros
};
```

## 7. Viñeta (capa superior)
```tsx
const Vignette: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none", background:
    "radial-gradient(ellipse at center, transparent 56%, rgba(0,0,0,0.22) 100%)" }}/>
);
```

## 8. Ken Burns — en cada imagen fija, sin excepción
```tsx
const KenBurns: React.FC<{src: string; zoomTo?: number}> = ({ src, zoomTo = 1.1 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [1, zoomTo],
    { easing: theme.ease.inOut });
  const pan = interpolate(frame, [0, durationInFrames], [0, -25]);
  return <Img src={staticFile(src)} style={{ width: "100%", height: "100%",
    objectFit: "cover", transform: `scale(${scale}) translateX(${pan}px)` }}/>;
};
```
Alternar zoom de entrada y de salida entre planos consecutivos. Para tarjetas redondeadas:
`borderRadius: 32, overflow: "hidden", border: "1px solid rgba(255,255,255,0.08)",
boxShadow: "0 40px 80px -20px rgba(0,0,0,0.6)"`.

## 9. Contador animado
```tsx
const value = interpolate(
  spring({ frame: frame - delay, fps, config: { damping: 30, stiffness: 60 } }),
  [0, 1], [0, target]);
<span style={{ fontVariantNumeric: "tabular-nums" }}>{value.toFixed(1)}%</span>
```
`tabular-nums` evita que el texto salte al cambiar los dígitos.

## 10. Destello / logo radial (rayos en stagger)
```tsx
const rays = 12;
{Array.from({ length: rays }).map((_, i) => {
  const p = spring({ frame: frame - delay - i * 1.2, fps,
    config: theme.spring.snappy });
  return <div key={i} style={{ position: "absolute", left: "50%", top: "50%",
    width: size * 0.085, height: size * 0.46 * p, background: theme.colors.primary,
    borderRadius: size, transformOrigin: "50% 0%",
    transform: `translateX(-50%) rotate(${(360 / rays) * i}deg) translateY(${size * 0.07}px)` }}/>;
})}
```
Envolver en un contenedor con escala en spring bouncy + rotación en spring smooth desde -120°,
y `filter: drop-shadow(0 0 ${size*0.25}px ${theme.colors.glow})`.

## 11. Salidas — más rápidas que las entradas
```tsx
const exitY = interpolate(frame, [durationInFrames - 12, durationInFrames - 2],
  [0, -42], { easing: theme.ease.in,
  extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const exitO = interpolate(frame, [durationInFrames - 12, durationInFrames - 2],
  [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
```
Aplicar a cada elemento visible o a un contenedor de escena.

## 12. Respiración en reposo (elementos en pantalla > 2 s)
```tsx
const breathe = 1 + Math.sin(frame / 22) * 0.015;          // escala
const float = Math.sin(frame / 30) * 3;                     // translateY px
const drift = interpolate(frame, [0, 300], [0, -20]);       // parallax lento
```

## 13. Parallax (3 capas, profundidad inmediata)
```tsx
const x = interpolate(frame, [0, 90], [0, -120], { easing: theme.ease.inOut });
<Bg style={{ transform: `translateX(${x * 0.3}px)` }}/>
<Mid style={{ transform: `translateX(${x * 0.6}px)` }}/>
<Fg style={{ transform: `translateX(${x}px)` }}/>
```

## 14. Transiciones
Librería (`npm i @remotion/transitions`, ya incluida en el template):
```tsx
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}><A/></TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={slide({ direction: "from-right" })}
    timing={springTiming({ durationInFrames: 12 })}/>
  <TransitionSeries.Sequence durationInFrames={150}><B/></TransitionSeries.Sequence>
</TransitionSeries>
```
A mano, 8–14 frames cada una:
- **Whip pan**: el fondo se desplaza 1500 px en 6 frames con `filter: blur(8px)` durante el
  movimiento; el corte se esconde a mitad del barrido.
- **Escala a través**: A escala a 1,3 y se desvanece, B escala 0,8→1 debajo.
- **Barrido con máscara**: una forma del color de marca cruza la pantalla; el corte va detrás.

## 15. Motion blur (todo lo que se mueva > 30 px/frame)
```tsx
import { Trail } from "@remotion/motion-blur";
<Trail layers={4} lagInFrames={0.4}><FastThing/></Trail>
```

## 16. Sincronización de audio y efectos
```tsx
import { Audio, Sequence, staticFile } from "remotion";
<Audio src={staticFile("music/musica.mp3")} volume={0.25}/>
<Sequence from={entranceFrame - 3}> {/* efecto 2–3 frames ANTES de que llegue el visual */}
  <Audio src={staticFile("sfx/whoosh.mp3")} volume={0.7}/>
</Sequence>
```
Cortar en el tiempo musical: framesPorTiempo = fps * 60 / BPM. Colocar cortes e impactos en
múltiplos de ese valor. Música de fondo −18 dB por debajo de efectos y voz.
Música, voz y efectos: skills de ElevenLabs `music`, `text-to-speech`, `sound-effects`.

## 17. Subtítulos sincronizados con la voz
Obtener las marcas de tiempo por palabra (skill `speech-to-text` de ElevenLabs, o Whisper)
y agruparlas con `@remotion/captions`:
```tsx
import { createTikTokStyleCaptions } from "@remotion/captions";
const { pages } = createTikTokStyleCaptions({ captions, combineTokensWithinMilliseconds: 1200 });
// renderizar cada página en una Sequence desde msToFrame(page.startMs),
// resaltar la palabra activa comparando el tiempo actual con sus marcas
```
Estilo: peso display grueso, 2–4 palabras por página, palabra activa en theme.colors.primary,
situada a ~65 % de la altura (dentro de la zona segura 9:16).
