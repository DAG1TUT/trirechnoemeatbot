'use client';

import { Suspense, useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';
import GlassSphere from './GlassSphere';

interface GlassSceneProps {
  thinking?: boolean;
  flashCount?: number;
  className?: string;
}

function FlashLight({ flashCount = 0 }: { flashCount: number }) {
  const lightRef = useRef<THREE.PointLight>(null);

  useEffect(() => {
    if (flashCount === 0 || !lightRef.current) return;

    gsap.timeline()
      .to(lightRef.current, {
        intensity: 5.5,
        duration: 0.14,
        ease: 'power2.out',
      })
      .to(lightRef.current, {
        intensity: 1.2,
        duration: 0.72,
        ease: 'power3.in',
      });
  }, [flashCount]);

  return <pointLight ref={lightRef} position={[-4, 2, -2]} intensity={1.2} color="#fde68a" />;
}

export default function GlassScene({ thinking = false, flashCount = 0, className }: GlassSceneProps) {
  return (
    <Canvas
      className={className}
      frameloop="always"
      shadows
      dpr={[1, 1.5]}
      camera={{ position: [0, 0, 4.5], fov: 38 }}
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance',
        toneMapping: 2,
        toneMappingExposure: 1.1,
      }}
      style={{ background: 'transparent' }}
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[3, 6, 3]}
          intensity={2.5}
          castShadow
          shadow-mapSize={[512, 512]}
        />
        <FlashLight flashCount={flashCount} />
        <pointLight position={[4, -2, 4]} intensity={0.8} color="#e0f2fe" />

        <GlassSphere thinking={thinking} flashCount={flashCount} />

        <ContactShadows
          position={[0, -1.6, 0]}
          opacity={0.12}
          scale={5}
          blur={2.5}
          far={2}
        />

        <Environment preset="studio" />
      </Suspense>
    </Canvas>
  );
}
