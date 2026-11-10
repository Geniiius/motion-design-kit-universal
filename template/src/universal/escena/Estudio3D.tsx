import React, { useLayoutEffect } from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { tema } from "../tema";

// Luz de entorno: es lo que hace que los materiales brillantes parezcan reales (reflejos, no solo sombreado).
export const Entorno: React.FC<{ intensidad?: number }> = ({ intensidad = 0.72 }) => {
  const { gl, scene } = useThree();
  useLayoutEffect(() => {
    const pm = new THREE.PMREMGenerator(gl);
    const env = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = intensidad;
    gl.toneMapping = THREE.ACESFilmicToneMapping;
    return () => {
      env.dispose();
      pm.dispose();
    };
  }, [gl, scene, intensidad]);
  return null;
};

export type Toma = { t: number; pos: [number, number, number]; mira: [number, number, number]; fov?: number; corte?: boolean };

// Pista de cámara separada del mundo. Se aplica durante el render para no ir un fotograma por detrás del dibujo.
export const Camara: React.FC<{ t: number; tomas: Toma[] }> = ({ t, tomas }) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  let i = 0;
  for (let k = 0; k < tomas.length; k++) if (tomas[k].t <= t) i = k;
  const a = tomas[i];
  const b = tomas[i + 1];
  // Un corte salta de golpe; lo demás viaja con curva suave
  const p = b && !b.corte ? interpolate(t, [a.t, b.t], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: tema.easing.inOut }) : 0;
  const mez = (u: number[], v: number[], k: number) => u[k] + (v[k] - u[k]) * p;
  const destino = b && !b.corte ? b : a;
  const deriva = Math.sin(t * 0.45) * 0.03;
  camera.position.set(mez(a.pos, destino.pos, 0) + deriva, mez(a.pos, destino.pos, 1) + deriva * 0.4, mez(a.pos, destino.pos, 2));
  camera.fov = (a.fov ?? 30) + ((destino.fov ?? 30) - (a.fov ?? 30)) * p;
  camera.near = 0.1;
  camera.far = 120;
  camera.updateProjectionMatrix();
  camera.lookAt(mez(a.mira, destino.mira, 0), mez(a.mira, destino.mira, 1), mez(a.mira, destino.mira, 2));
  return null;
};

export const SetEstudio: React.FC<{ color?: string }> = ({ color = tema.estudio.fondo }) => (
  <>
    <color attach="background" args={[color]} />
    <fog attach="fog" args={[color, 11, 30]} />
    <hemisphereLight args={["#FFFFFF", "#9AA6C4", 0.5]} />
    <directionalLight position={[3.4, 7, 5]} intensity={2.3} color="#FFF4E4" castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-camera-left={-5} shadow-camera-right={5} shadow-camera-top={5} shadow-camera-bottom={-5} shadow-radius={9} shadow-bias={-0.0004} />
    <directionalLight position={[-5, 3, 2]} intensity={0.8} color="#BBD0FF" />
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.26, 0]} receiveShadow>
      <planeGeometry args={[90, 90]} />
      <meshStandardMaterial color={tema.estudio.suelo} roughness={0.36} metalness={0.05} />
    </mesh>
    {/* Arcos de fondo: dan profundidad y paralaje cuando se mueve la cámara */}
    {[
      [-4.6, -5, 3.1],
      [4.9, -7, 3.8],
      [0.6, -11, 5.2],
    ].map(([x, z, r], i) => (
      <mesh key={i} position={[x, -1.26, z]}>
        <torusGeometry args={[r, 0.34, 24, 72, Math.PI]} />
        <meshStandardMaterial color={tema.estudio.arco} roughness={0.5} />
      </mesh>
    ))}
  </>
);

export const useTiempo = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};
