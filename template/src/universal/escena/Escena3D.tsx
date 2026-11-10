import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { z } from "zod";
import { Acabado, entrada } from "../capas";
import { bocaEn, poseEn } from "../personajes/gestos";
import { Nodo } from "../personajes/Nodo";
import { medida, tema } from "../tema";
import { Camara, Entorno, Toma, useTiempo } from "./Estudio3D";

export const escenaSchema = z.object({ titulo: z.string(), subtitulo: z.string(), cinemascope: z.boolean() });
export type EscenaProps = z.infer<typeof escenaSchema>;
export const escenaDefaults: EscenaProps = { titulo: "", subtitulo: "", cinemascope: true };

const c = tema.cine;

// Objeto héroe procedural: lo que construye el look es la luz, no la geometría.
const Heroe: React.FC<{ t: number }> = ({ t }) => {
  const m = useMemo(
    () => ({
      cuerpo: new THREE.MeshPhysicalMaterial({ color: c.oscuro, roughness: 0.22, metalness: 0.75, clearcoat: 1, clearcoatRoughness: 0.08 }),
      aro: new THREE.MeshStandardMaterial({ color: c.metal, roughness: 0.16, metalness: 1 }),
      nucleo: new THREE.MeshStandardMaterial({ color: "#000000", emissive: c.brillo, emissiveIntensity: 2.6 }),
      forma: new RoundedBoxGeometry(1.5, 2.3, 0.42, 8, 0.2),
    }),
    [],
  );
  const pulso = 2.2 + Math.sin(t * 1.4) * 0.6;
  m.nucleo.emissiveIntensity = pulso;
  return (
    <group rotation={[0.04, t * 0.08 - 0.42, 0.02]} position={[0, 0.25, 0]}>
      <mesh geometry={m.forma} material={m.cuerpo} castShadow />
      <mesh material={m.aro} position={[0, 0.2, 0.22]}>
        <torusGeometry args={[0.42, 0.035, 20, 96]} />
      </mesh>
      <mesh material={m.nucleo} position={[0, 0.2, 0.23]} scale={[0.24, 0.24, 0.03]}>
        <sphereGeometry args={[1, 32, 24]} />
      </mesh>
      <pointLight position={[0, 0.2, 0.9]} color={c.brillo} intensity={pulso * 1.6} distance={6} />
    </group>
  );
};

// Halos suaves detrás del héroe: dan atmósfera sin los bordes duros de un cono geométrico.
const Halo: React.FC<{ pos: [number, number, number]; tam: number; color: string; fuerza: number }> = ({ pos, tam, color, fuerza }) => {
  const textura = useMemo(() => {
    const lienzo = document.createElement("canvas");
    lienzo.width = lienzo.height = 256;
    const g = lienzo.getContext("2d") as CanvasRenderingContext2D;
    const d = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    d.addColorStop(0, "rgba(255,255,255,1)");
    d.addColorStop(0.4, "rgba(255,255,255,0.32)");
    d.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = d;
    g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(lienzo);
  }, []);
  return (
    <sprite position={pos} scale={[tam, tam, 1]}>
      <spriteMaterial map={textura} color={color} opacity={fuerza} transparent blending={THREE.AdditiveBlending} depthWrite={false} fog={false} />
    </sprite>
  );
};

const SetCine: React.FC = () => (
  <>
    <color attach="background" args={[c.fondo]} />
    <fog attach="fog" args={[c.fondo, 8, 24]} />
    <spotLight position={[4.5, 7, 4]} angle={0.42} penumbra={0.9} intensity={70} color={c.brillo} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} />
    <spotLight position={[-5.5, 5, 2]} angle={0.5} penumbra={1} intensity={55} color={c.frio} />
    <Halo pos={[2.6, 1.3, -5]} tam={12} color={c.brillo} fuerza={0.3} />
    <Halo pos={[-3.2, 0.7, -6]} tam={13} color={c.frio} fuerza={0.26} />
    {/* Suelo pulido: semitransparente sobre un reflejo del héroe */}
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.1, 0]} receiveShadow>
      <planeGeometry args={[70, 70]} />
      <meshStandardMaterial color="#0A0D14" roughness={0.26} metalness={0.5} transparent opacity={0.84} />
    </mesh>
  </>
);

const Letras: React.FC<{ titulo: string; subtitulo: string; inicio: number }> = ({ titulo, subtitulo, inicio }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { u } = medida(width, height);
  if (!titulo) return null;
  const a = entrada(frame, inicio, fps, 0.9);
  const b = entrada(frame, inicio + 0.45, fps, 0.8);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 150 * u }}>
      <div style={{ opacity: a, transform: `translateY(${(1 - a) * 18}px)`, letterSpacing: (14 - a * 4) * u, color: c.tinta, fontFamily: tema.fuentes.display, fontWeight: 500, fontSize: 58 * u, textTransform: "uppercase", textAlign: "center" }}>{titulo}</div>
      {subtitulo ? <div style={{ opacity: b, marginTop: 12 * u, color: c.metal, fontFamily: tema.fuentes.body, fontSize: 28 * u, textAlign: "center" }}>{subtitulo}</div> : null}
    </AbsoluteFill>
  );
};

// Bandas 2,39:1 y etalonaje: parte del lenguaje de cine, no una promesa de calidad de superproducción.
const Encuadre: React.FC<{ activo: boolean }> = ({ activo }) => {
  const { width, height } = useVideoConfig();
  if (!activo || height > width) return null;
  const banda = (height - width / 2.39) / 2;
  return (
    <>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: banda, background: "#000" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: banda, background: "#000" }} />
    </>
  );
};

const TOMAS_CINE: Toma[] = [
  { t: 0, pos: [0.5, 0.05, 11], mira: [0, 0.3, 0], fov: 22 },
  { t: 4, pos: [-3.2, 0.5, 7], mira: [0, 0.35, 0], fov: 26 },
  { t: 8, pos: [-2.6, 1.3, 5.6], mira: [0, 0.3, 0], fov: 30 },
];

export const Escena3D: React.FC<EscenaProps> = ({ titulo, subtitulo, cinemascope }) => {
  const t = useTiempo();
  const { width, height } = useVideoConfig();
  const k = height > width ? 1.6 : 1;
  const tomas = TOMAS_CINE.map((x) => ({ ...x, pos: [x.pos[0], x.pos[1], x.pos[2] * k] as [number, number, number] }));
  return (
    <AbsoluteFill style={{ background: c.fondo }}>
      <AbsoluteFill style={{ filter: "contrast(1.08) saturate(1.06)" }}>
        <ThreeCanvas width={width} height={height} shadows gl={{ antialias: true, preserveDrawingBuffer: true }}>
          <Camara t={t} tomas={tomas} />
          <Entorno intensidad={0.32} />
          <SetCine />
          <Heroe t={t} />
          <group position={[0, -2.2, 0]} scale={[1, -1, 1]}>
            <Heroe t={t} />
          </group>
        </ThreeCanvas>
      </AbsoluteFill>
      <Letras titulo={titulo} subtitulo={subtitulo} inicio={3.2} />
      <Acabado vineta={0.6} grano={0.07} />
      <Encuadre activo={cinemascope} />
    </AbsoluteFill>
  );
};

export const hibridoSchema = z.object({ clip: z.string(), titulo: z.string(), subtitulo: z.string() });
export type HibridoProps = z.infer<typeof hibridoSchema>;
export const hibridoDefaults: HibridoProps = { clip: "universal/medios/clip-a.mp4", titulo: "", subtitulo: "" };

// Rodaje + 3D: el vídeo sigue siendo el vídeo, el personaje se compone encima con fondo transparente.
export const Hibrido: React.FC<HibridoProps> = ({ clip, titulo, subtitulo }) => {
  const frame = useCurrentFrame();
  const t = useTiempo();
  const { width, height } = useVideoConfig();
  const zoom = interpolate(frame, [0, 180], [1.02, 1.09], { extrapolateRight: "clamp", easing: tema.easing.inOut });
  const pose = poseEn(t, [{ tipo: "saludar", inicio: 0.6, fin: 2.6, lado: 1 }, { tipo: "senalar", inicio: 3, fin: 4.8, lado: -1 }], 0);
  return (
    <AbsoluteFill style={{ background: c.fondo }}>
      <AbsoluteFill style={{ transform: `scale(${zoom})`, filter: "contrast(1.08) saturate(0.92) sepia(0.08)" }}>
        <OffthreadVideo src={staticFile(clip)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </AbsoluteFill>
      <ThreeCanvas width={width} height={height} shadows gl={{ antialias: true, alpha: true, preserveDrawingBuffer: true }}>
        <Camara t={t} tomas={[{ t: 0, pos: [0, 0.4, 13], mira: [0, 0, 0], fov: 26 }, { t: 6, pos: [-1.1, 0.5, 11], mira: [0, 0, 0], fov: 26 }]} />
        <Entorno intensidad={0.9} />
        <directionalLight position={[3, 5, 5]} intensity={2.4} color="#FFF0DE" />
        <Nodo pose={pose} boca={bocaEn(t, [], [])} posicion={[width > height ? 2.3 : 0, -0.5, 0]} />
      </ThreeCanvas>
      <Letras titulo={titulo} subtitulo={subtitulo} inicio={0.9} />
      <Acabado vineta={0.5} grano={0.06} />
      <Encuadre activo />
    </AbsoluteFill>
  );
};
