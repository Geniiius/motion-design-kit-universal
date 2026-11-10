import React, { useEffect, useMemo, useState } from "react";
import { AbsoluteFill, Audio, CalculateMetadataFunction, cancelRender, continueRender, delayRender, staticFile, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { GLTF, GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { z } from "zod";
import { Acabado, Subtitulo } from "../capas";
import { Camara, Entorno, SetEstudio, useTiempo } from "../escena/Estudio3D";
import { medida, tema } from "../tema";

// Importa un personaje .glb con licencia conocida: reproduce sus animaciones de forma determinista.
// Si el modelo no tiene formas de boca, el habla se reparte en un leve movimiento de cabeza.
export const glbSchema = z.object({
  modelo: z.string().describe("Ruta del .glb en /public"),
  duracion: z.number(),
  clips: z.array(z.object({ nombre: z.string(), inicio: z.number(), fin: z.number(), expresion: z.string().optional() })),
  voz: z.string(),
  words: z.array(z.object({ text: z.string(), start: z.number(), end: z.number() })),
  envolvente: z.array(z.number()),
  escala: z.number(),
  altura: z.number(),
});
export type GlbProps = z.infer<typeof glbSchema>;
export const glbDefaults: GlbProps = {
  modelo: "universal/modelos/RobotExpressive.glb",
  duracion: 6,
  clips: [
    { nombre: "Walking", inicio: 0, fin: 2 },
    { nombre: "Wave", inicio: 2, fin: 4.2, expresion: "Surprised" },
    { nombre: "ThumbsUp", inicio: 4.2, fin: 6 },
  ],
  voz: "",
  words: [],
  envolvente: [],
  escala: 0.5,
  altura: -1.26,
};
export const calculateGlb: CalculateMetadataFunction<GlbProps> = ({ props }) => ({ durationInFrames: Math.ceil(props.duracion * 30), fps: 30 });

const FUNDIDO = 0.25;

const Modelo: React.FC<{ gltf: GLTF; t: number; clips: GlbProps["clips"]; amp: number; escala: number; altura: number }> = ({ gltf, t, clips, amp, escala, altura }) => {
  const { mixer, acciones, cabeza, cuerpos } = useMemo(() => {
    const mx = new THREE.AnimationMixer(gltf.scene);
    const ac = new Map(gltf.animations.map((a) => [a.name, mx.clipAction(a)]));
    ac.forEach((a) => a.play());
    const malla: THREE.Mesh[] = [];
    let cab: THREE.Object3D | null = null;
    gltf.scene.traverse((o) => {
      o.castShadow = true;
      if ((o as THREE.Mesh).isMesh) malla.push(o as THREE.Mesh);
      if (!cab && /head/i.test(o.name)) cab = o;
    });
    return { mixer: mx, acciones: ac, cabeza: cab as THREE.Object3D | null, cuerpos: malla };
  }, [gltf]);
  // Cada fotograma se calcula desde t: el resultado no depende del orden de renderizado.
  const activo = clips.find((c) => t >= c.inicio && t < c.fin) ?? clips[clips.length - 1];
  acciones.forEach((a, nombre) => {
    const c = clips.find((x) => x.nombre === nombre);
    if (!c || t < c.inicio - FUNDIDO || t > c.fin + FUNDIDO) return void a.setEffectiveWeight(0);
    const entra = Math.min(1, (t - (c.inicio - FUNDIDO)) / FUNDIDO);
    const sale = Math.min(1, (c.fin + FUNDIDO - t) / FUNDIDO);
    a.enabled = true;
    a.setEffectiveTimeScale(0);
    a.setEffectiveWeight(c === clips[0] ? sale : Math.min(entra, sale));
    a.time = (t - c.inicio) % a.getClip().duration;
    if (a.time < 0) a.time = 0;
  });
  mixer.update(0);
  if (cabeza) cabeza.rotation.x += amp * 0.16;
  cuerpos.forEach((m) => {
    const d = m.morphTargetDictionary;
    if (!d || !m.morphTargetInfluences) return;
    m.morphTargetInfluences.fill(0);
    if (activo.expresion && d[activo.expresion] !== undefined) m.morphTargetInfluences[d[activo.expresion]] = 0.7;
  });
  return <primitive object={gltf.scene} scale={escala} position={[0, altura, 0]} />;
};

export const PersonajeGLB: React.FC<GlbProps> = ({ modelo, duracion, clips, voz, words, envolvente, escala, altura }) => {
  const t = useTiempo();
  const { width, height } = useVideoConfig();
  const { vertical } = medida(width, height);
  const [gltf, setGltf] = useState<GLTF | null>(null);
  const [espera] = useState(() => delayRender(`Cargando ${modelo}`));
  useEffect(() => {
    new GLTFLoader().load(
      staticFile(modelo),
      (g) => {
        setGltf(g);
        continueRender(espera);
      },
      undefined,
      (e) => cancelRender(e instanceof Error ? e : new Error(String(e))),
    );
  }, [modelo, espera]);
  const k = vertical ? 1.5 : 1;
  const tomas = [
    { t: 0, pos: [-2.2, 1, 9.2 * k] as [number, number, number], mira: [0, 0.05, 0] as [number, number, number], fov: 28 },
    { t: duracion, pos: [1.2, 0.7, 6.8 * k] as [number, number, number], mira: [0, 0.1, 0] as [number, number, number], fov: 28 },
  ];
  return (
    <AbsoluteFill style={{ background: tema.estudio.fondo }}>
      {voz ? <Audio src={staticFile(voz)} /> : null}
      <ThreeCanvas width={width} height={height} shadows gl={{ antialias: true, preserveDrawingBuffer: true }}>
        <Camara t={t} tomas={tomas} />
        <Entorno />
        <SetEstudio />
        {gltf ? <Modelo gltf={gltf} t={t} clips={clips} amp={envolvente[Math.floor(t * 30)] ?? 0} escala={escala} altura={altura} /> : null}
      </ThreeCanvas>
      <Subtitulo words={words} color={tema.estudio.sub} apagado="rgba(255,255,255,0.45)" fondo={tema.estudio.subFondo} />
      <Acabado vineta={0.07} grano={0.03} />
    </AbsoluteFill>
  );
};
