import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { entrada, salida } from "../capas";
import { medida, tema } from "../tema";

// Piezas reutilizables del explainer. Cada una recibe datos y su ventana de tiempo [inicio, fin] en segundos.
type Ventana = { inicio: number; fin: number };
const c = tema.datos;
const numero = (v: number, decimales: number, coma?: boolean) => (coma ? v.toFixed(decimales).replace(".", ",") : v.toFixed(decimales));

const usePieza = ({ inicio, fin }: Ventana) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const visible = t >= inicio - 0.02 && t <= fin + 0.02;
  return { frame, fps, t, width, height, ...medida(width, height), visible, sale: salida(frame, fin, fps) };
};

export const ConceptReveal: React.FC<Ventana & { rotulo: string; titulo: string; definicion: string }> = ({ inicio, fin, rotulo, titulo, definicion }) => {
  const { frame, fps, u, visible, sale, t } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.55);
  const b = entrada(frame, inicio + 0.35, fps, 0.5);
  const d = entrada(frame, inicio + 0.8, fps, 0.5);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 90 * u, opacity: sale }}>
      <div style={{ textAlign: "center", transform: `scale(${1 + (t - inicio) * 0.006})` }}>
        <div style={{ opacity: a, transform: `translateY(${(1 - a) * 18}px)`, color: c.acento, fontFamily: tema.fuentes.body, fontWeight: 600, fontSize: 30 * u, letterSpacing: 5 * u, textTransform: "uppercase" }}>{rotulo}</div>
        <div style={{ opacity: b, transform: `translateY(${(1 - b) * 34}px) scale(${1.08 - b * 0.08})`, filter: `blur(${(1 - b) * 8}px)`, color: c.tinta, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 104 * u, lineHeight: 1.06, margin: `${22 * u}px 0` }}>{titulo}</div>
        <div style={{ opacity: d, transform: `translateY(${(1 - d) * 18}px)`, color: c.suave, fontFamily: tema.fuentes.body, fontSize: 36 * u, maxWidth: 1100 * u, margin: "0 auto" }}>{definicion}</div>
      </div>
    </AbsoluteFill>
  );
};

export type Punto = { x: number; y: number };

// Línea que se dibuja con el tiempo; el contador sigue a la punta y no se inventa ningún valor intermedio.
export const DataChart: React.FC<Ventana & { serie: Punto[]; unidad: string; rotulo: string; inicioDibujo?: number; finDibujo?: number; decimales?: number; coma?: boolean }> = ({ inicio, fin, serie, unidad, rotulo, inicioDibujo, finDibujo, decimales = 1, coma }) => {
  const { frame, fps, u, visible, sale, width, height, vertical, t } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.45);
  const W = width - (vertical ? 120 : 260) * u;
  const H = height * (vertical ? 0.36 : 0.5);
  const xs = serie.map((p) => p.x);
  const ys = serie.map((p) => p.y);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const px = (x: number) => ((x - x0) / (x1 - x0)) * W;
  const py = (y: number) => H - ((y - y0) / (y1 - y0)) * H * 0.92 - H * 0.04;
  const p = interpolate(t, [inicioDibujo ?? inicio + 0.3, finDibujo ?? fin - 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.sin) });
  const cuenta = 1 + p * (serie.length - 1);
  const n = Math.floor(cuenta);
  const f = cuenta - n;
  const visibles = serie.slice(0, n);
  const sig = serie[Math.min(n, serie.length - 1)];
  const ult = visibles[visibles.length - 1];
  const punta = { x: ult.x + (sig.x - ult.x) * f, y: ult.y + (sig.y - ult.y) * f };
  const camino = [...visibles, punta].map((q, i) => `${i ? "L" : "M"}${px(q.x).toFixed(1)} ${py(q.y).toFixed(1)}`).join(" ");
  const rejilla = 5;
  const paso = Math.ceil((y1 - y0) / rejilla / 10) * 10;
  const lineas: number[] = [];
  for (let v = Math.ceil(y0 / paso) * paso; v <= y1; v += paso) lineas.push(v);
  const anios: number[] = [];
  for (let v = Math.ceil(x0 / 10) * 10; v <= x1; v += vertical ? 20 : 10) anios.push(v);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingBottom: (vertical ? 300 : 120) * u, opacity: a * sale, transform: `translateY(${(1 - a) * 26}px)` }}>
      <div style={{ position: "relative", width: W, height: H + 150 * u, transform: `scale(${1 + (t - inicio) * 0.004})` }}>
        <div style={{ color: c.suave, fontFamily: tema.fuentes.body, fontSize: 28 * u, marginBottom: 8 * u }}>{rotulo}</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 14 * u, marginBottom: 14 * u }}>
          <span style={{ color: c.acento, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 92 * u, lineHeight: 1 }}>{numero(punta.y, decimales, coma)}</span>
          <span style={{ color: c.tinta, fontFamily: tema.fuentes.body, fontSize: 34 * u }}>{unidad}</span>
          <span style={{ color: c.suave, fontFamily: tema.fuentes.body, fontSize: 34 * u, marginLeft: 18 * u }}>{Math.floor(punta.x)}</span>
        </div>
        <svg width={W} height={H} style={{ overflow: "visible" }}>
          {lineas.map((v) => (
            <g key={v}>
              <line x1={0} x2={W} y1={py(v)} y2={py(v)} stroke={c.linea} strokeWidth={1.5 * u} />
              <text x={0} y={py(v) - 8 * u} fill={c.suave} fontSize={22 * u} fontFamily={tema.fuentes.body}>{v}</text>
            </g>
          ))}
          {anios.map((v) => (
            <text key={v} x={px(v)} y={H + 34 * u} fill={c.suave} fontSize={24 * u} textAnchor="middle" fontFamily={tema.fuentes.body}>{v}</text>
          ))}
          <path d={camino} fill="none" stroke={c.acento} strokeWidth={6 * u} strokeLinecap="round" strokeLinejoin="round" />
          <circle cx={px(punta.x)} cy={py(punta.y)} r={11 * u} fill={c.acento2} />
          <circle cx={px(punta.x)} cy={py(punta.y)} r={(20 + Math.sin(t * 5) * 3) * u} fill="none" stroke={c.acento2} strokeOpacity={0.5} strokeWidth={2.5 * u} />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

export const Comparison: React.FC<Ventana & { rotulo: string; unidad: string; barras: { etiqueta: string; valor: number; nota?: string }[]; coma?: boolean }> = ({ inicio, fin, rotulo, unidad, barras, coma }) => {
  const { frame, fps, u, visible, sale, vertical } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.4);
  const tope = Math.max(...barras.map((b) => b.valor));
  const ancho = (vertical ? 760 : 1180) * u;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sale }}>
      <div style={{ width: ancho }}>
        <div style={{ opacity: a, color: c.tinta, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 54 * u, marginBottom: 34 * u, lineHeight: 1.12 }}>{rotulo}</div>
        {barras.map((b, i) => {
          const p = entrada(frame, inicio + 0.25 + i * 0.16, fps, 0.65);
          const destacada = b.valor === tope;
          return (
            <div key={b.etiqueta} style={{ marginBottom: 20 * u, opacity: Math.min(1, p * 1.6), transform: `translateX(${(1 - p) * -24}px)` }}>
              <div style={{ display: "flex", justifyContent: "space-between", color: c.suave, fontFamily: tema.fuentes.body, fontSize: 28 * u, marginBottom: 6 * u }}>
                <span>{b.etiqueta}</span>
                <span style={{ color: destacada ? c.acento2 : c.tinta, fontWeight: 600 }}>{numero(b.valor * p, 2, coma)} {unidad}</span>
              </div>
              <div style={{ height: 30 * u, borderRadius: 15 * u, background: c.linea, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${(b.valor / tope) * 100 * p}%`, borderRadius: 15 * u, background: destacada ? c.acento2 : c.acento }} />
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const Timeline: React.FC<Ventana & { rotulo: string; hitos: { fecha: string; texto: string }[] }> = ({ inicio, fin, rotulo, hitos }) => {
  const { frame, fps, u, visible, sale, t } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.4);
  const reparto = (fin - inicio - 0.6) / hitos.length;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sale, padding: 70 * u }}>
      <div style={{ maxWidth: 1300 * u, width: "100%" }}>
        <div style={{ opacity: a, color: c.tinta, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 54 * u, marginBottom: 30 * u }}>{rotulo}</div>
        <div style={{ position: "relative", paddingLeft: 46 * u }}>
          <div style={{ position: "absolute", left: 11 * u, top: 8 * u, bottom: 8 * u, width: 4 * u, background: c.linea, transformOrigin: "top", transform: `scaleY(${interpolate(t, [inicio, fin - 0.8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: tema.easing.inOut })})` }} />
          {hitos.map((h, i) => {
            const p = entrada(frame, inicio + 0.2 + i * reparto, fps, 0.42);
            return (
              <div key={h.fecha} style={{ position: "relative", marginBottom: 28 * u, opacity: p, transform: `translateY(${(1 - p) * 20}px)` }}>
                <div style={{ position: "absolute", left: -44 * u, top: 8 * u, width: 26 * u, height: 26 * u, borderRadius: "50%", background: c.acento, transform: `scale(${0.4 + p * 0.6})` }} />
                <div style={{ color: c.acento, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 36 * u }}>{h.fecha}</div>
                <div style={{ color: c.tinta, fontFamily: tema.fuentes.body, fontSize: 31 * u, lineHeight: 1.3 }}>{h.texto}</div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const FlowDiagram: React.FC<Ventana & { rotulo: string; pasos: string[] }> = ({ inicio, fin, rotulo, pasos }) => {
  const { frame, fps, u, visible, sale, vertical } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.4);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sale, padding: 60 * u }}>
      <div style={{ textAlign: "center", width: "100%" }}>
        <div style={{ opacity: a, color: c.tinta, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 54 * u, marginBottom: 44 * u }}>{rotulo}</div>
        <div style={{ display: "flex", flexDirection: vertical ? "column" : "row", alignItems: "center", justifyContent: "center", gap: 14 * u }}>
          {pasos.map((p, i) => {
            const e = entrada(frame, inicio + 0.25 + i * 0.32, fps, 0.42);
            const flecha = entrada(frame, inicio + 0.45 + i * 0.32, fps, 0.3);
            return (
              <React.Fragment key={p}>
                <div style={{ opacity: e, transform: `translateY(${(1 - e) * 22}px) scale(${0.9 + e * 0.1})`, background: c.panel, border: `${2 * u}px solid ${i === pasos.length - 1 ? c.acento2 : c.linea}`, borderRadius: 20 * u, padding: `${24 * u}px ${28 * u}px`, width: (vertical ? 640 : 380) * u, color: c.tinta, fontFamily: tema.fuentes.body, fontWeight: 600, fontSize: 32 * u, lineHeight: 1.22 }}>{p}</div>
                {i < pasos.length - 1 ? (
                  <svg width={46 * u} height={46 * u} viewBox="0 0 46 46" style={{ opacity: flecha, transform: vertical ? "rotate(90deg)" : undefined, flexShrink: 0 }}>
                    <path d="M6 23 H36 M26 12 L37 23 L26 34" stroke={c.acento} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : null}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const StepByStepExplainer: React.FC<Ventana & { rotulo: string; pasos: string[] }> = ({ inicio, fin, rotulo, pasos }) => {
  const { frame, fps, u, visible, sale } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.4);
  const reparto = (fin - inicio - 0.5) / pasos.length;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sale, padding: 70 * u }}>
      <div style={{ maxWidth: 1240 * u, width: "100%" }}>
        <div style={{ opacity: a, color: c.tinta, fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 54 * u, marginBottom: 32 * u }}>{rotulo}</div>
        {pasos.map((p, i) => {
          const e = entrada(frame, inicio + 0.15 + i * reparto, fps, 0.42);
          return (
            <div key={p} style={{ display: "flex", gap: 22 * u, alignItems: "flex-start", marginBottom: 22 * u, opacity: e, transform: `translateX(${(1 - e) * 30}px)` }}>
              <div style={{ flexShrink: 0, width: 58 * u, height: 58 * u, borderRadius: "50%", background: c.acento, color: c.fondo, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: tema.fuentes.display, fontWeight: 700, fontSize: 30 * u }}>{i + 1}</div>
              <div style={{ color: c.tinta, fontFamily: tema.fuentes.body, fontSize: 34 * u, lineHeight: 1.3, paddingTop: 6 * u }}>{p}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// Fuente, unidad, fecha e incertidumbre: se muestran siempre, no son letra pequeña opcional.
export const FichaFuente: React.FC<Ventana & { rotulo: string; lineas: string[] }> = ({ inicio, fin, rotulo, lineas }) => {
  const { frame, fps, u, visible, sale } = usePieza({ inicio, fin });
  if (!visible) return null;
  const a = entrada(frame, inicio, fps, 0.45);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: sale, padding: 70 * u }}>
      <div style={{ opacity: a, transform: `translateY(${(1 - a) * 20}px)`, background: c.panel, border: `${2 * u}px solid ${c.linea}`, borderRadius: 26 * u, padding: 50 * u, maxWidth: 1320 * u }}>
        <div style={{ color: c.acento, fontFamily: tema.fuentes.body, fontWeight: 600, fontSize: 28 * u, letterSpacing: 4 * u, textTransform: "uppercase", marginBottom: 22 * u }}>{rotulo}</div>
        {lineas.map((l) => (
          <div key={l} style={{ color: c.tinta, fontFamily: tema.fuentes.body, fontSize: 32 * u, lineHeight: 1.36, marginBottom: 10 * u, overflowWrap: "anywhere" }}>{l}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
