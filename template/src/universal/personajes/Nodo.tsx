import React, { useMemo } from "react";
import * as THREE from "three";
import biblia from "./nodo.json";
import type { Boca, Pose } from "./gestos";

// Nodo: personaje persistente. La paleta y las proporciones salen de su ficha (nodo.json), en todos los planos.
const c = biblia.paleta;

const useMateriales = () =>
  useMemo(
    () => ({
      cuerpo: new THREE.MeshPhysicalMaterial({ color: c.cuerpo, roughness: 0.28, metalness: 0.05, clearcoat: 1, clearcoatRoughness: 0.08 }),
      cara: new THREE.MeshPhysicalMaterial({ color: c.cara, roughness: 0.42, clearcoat: 0.45, clearcoatRoughness: 0.3 }),
      ojo: new THREE.MeshPhysicalMaterial({ color: c.ojo, roughness: 0.06, clearcoat: 1, clearcoatRoughness: 0.03 }),
      brillo: new THREE.MeshBasicMaterial({ color: "#FFFFFF" }),
      boca: new THREE.MeshStandardMaterial({ color: c.boca, roughness: 0.65 }),
      lengua: new THREE.MeshStandardMaterial({ color: c.lengua, roughness: 0.55 }),
      mano: new THREE.MeshPhysicalMaterial({ color: c.mano, roughness: 0.32, clearcoat: 0.9, clearcoatRoughness: 0.12 }),
      mejilla: new THREE.MeshStandardMaterial({ color: c.mejilla, roughness: 0.8, transparent: true, opacity: 0.75 }),
      ceja: new THREE.MeshStandardMaterial({ color: c.ojo, roughness: 0.6 }),
      antena: new THREE.MeshStandardMaterial({ color: "#39435F", roughness: 0.35, metalness: 0.8 }),
    }),
    [],
  );

const Mano: React.FC<{ p: [number, number, number]; rot: number; lado: 1 | -1; m: THREE.Material }> = ({ p, rot, lado, m }) => (
  <group position={p} rotation={[0, 0, rot]}>
    <mesh material={m} scale={[0.23, 0.29, 0.17]} castShadow>
      <sphereGeometry args={[1, 32, 24]} />
    </mesh>
    <mesh material={m} position={[lado * -0.2, -0.04, 0.03]} rotation={[0, 0, lado * 0.8]} scale={[0.08, 0.14, 0.08]} castShadow>
      <sphereGeometry args={[1, 20, 16]} />
    </mesh>
  </group>
);

export const Nodo: React.FC<{ pose: Pose; boca: Boca; energia?: number; escala?: number; posicion?: [number, number, number] }> = ({ pose, boca, energia = 0, escala = 1, posicion = [0, 0, 0] }) => {
  const m = useMateriales();
  const bocaAlto = 0.012 + boca.abre * 0.135;
  const bocaAncho = 0.11 + boca.ancho * 0.13;
  return (
    <group position={[posicion[0] + pose.x, posicion[1] + pose.y + pose.salto, posicion[2]]} rotation={[0, pose.giro, pose.inclina]} scale={[escala * (2 - pose.aplasta), escala * pose.aplasta, escala * (2 - pose.aplasta)]}>
      <mesh material={m.cuerpo} scale={[0.95, 1.05, 0.86]} castShadow>
        <sphereGeometry args={[1, 160, 120]} />
      </mesh>
      {/* cara */}
      <mesh material={m.cara} position={[0, 0.14, 0.44]} scale={[0.73, 0.72, 0.46]}>
        <sphereGeometry args={[1, 160, 120]} />
      </mesh>
      {[-1, 1].map((s) => (
        <group key={s} position={[s * 0.27, 0.35, 0.82]}>
          <mesh material={m.ojo} scale={[0.14, 0.17 * Math.max(0.1, pose.ojos), 0.075]}>
            <sphereGeometry args={[1, 32, 24]} />
          </mesh>
          {pose.ojos > 0.5 ? (
            <mesh material={m.brillo} position={[0.05 + pose.mira[0], 0.07 + pose.mira[1], 0.07]} scale={0.038}>
              <sphereGeometry args={[1, 16, 12]} />
            </mesh>
          ) : null}
          <mesh material={m.ceja} position={[0, 0.26 + pose.ceja * 0.06, -0.09]} rotation={[0, 0, s * (-0.12 + pose.ceja * -0.14)]} scale={[0.14, 0.024, 0.024]}>
            <sphereGeometry args={[1, 16, 12]} />
          </mesh>
          <mesh material={m.mejilla} position={[s * 0.1, -0.22, -0.02]} scale={[0.1, 0.06, 0.018]}>
            <sphereGeometry args={[1, 18, 14]} />
          </mesh>
        </group>
      ))}
      {/* boca: su forma viene de los visemas reales de la voz */}
      <group position={[0, -0.1, 0.865]}>
        <mesh material={m.boca} scale={[bocaAncho, bocaAlto, 0.03]}>
          <sphereGeometry args={[1, 32, 24]} />
        </mesh>
        {boca.abre > 0.4 ? (
          <mesh material={m.lengua} position={[0, -bocaAlto * 0.5, 0.012]} scale={[bocaAncho * 0.62, bocaAlto * 0.42, 0.024]}>
            <sphereGeometry args={[1, 20, 14]} />
          </mesh>
        ) : null}
      </group>
      {/* antena */}
      <mesh material={m.antena} position={[0, 1.15, 0]}>
        <cylinderGeometry args={[0.02, 0.028, 0.3, 14]} />
      </mesh>
      <mesh position={[0, 1.36, 0]} scale={0.095 + energia * 0.025}>
        <sphereGeometry args={[1, 24, 18]} />
        <meshStandardMaterial color={c.antena} emissive={c.antena} emissiveIntensity={0.55 + energia * 1.3} roughness={0.3} />
      </mesh>
      <Mano p={pose.manoD} rot={pose.rotD} lado={1} m={m.mano} />
      <Mano p={pose.manoI} rot={pose.rotI} lado={-1} m={m.mano} />
      {[-1, 1].map((s) => (
        <mesh key={s} material={m.mano} position={[s * 0.38, -1.13 - pose.salto * 0.12, 0.14]} scale={[0.26, 0.11, 0.34]} castShadow>
          <sphereGeometry args={[1, 28, 20]} />
        </mesh>
      ))}
    </group>
  );
};
