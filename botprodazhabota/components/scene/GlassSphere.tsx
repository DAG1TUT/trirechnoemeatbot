'use client';

import { useRef, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { MeshTransmissionMaterial, BakeShadows } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';
import { getScrollMorphState } from '@/hooks/useScrollMorph';

interface GlassSphereProps {
  thinking?: boolean;
  flashCount?: number;
}

export default function GlassSphere({ thinking = false, flashCount = 0 }: GlassSphereProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const matRef = useRef<{
    roughness: number;
    thickness: number;
    distortion: number;
  }>(null);

  const pulseRef = useRef<gsap.core.Tween | null>(null);
  const flashTlRef = useRef<gsap.core.Timeline | null>(null);
  const { gl } = useThree();

  // Thinking state: pulse scale + roughness
  useEffect(() => {
    if (!meshRef.current) return;

    if (thinking) {
      pulseRef.current = gsap.to(meshRef.current.scale, {
        x: 1.08,
        y: 1.08,
        z: 1.08,
        duration: 0.6,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
      });
    } else {
      pulseRef.current?.kill();
      gsap.to(meshRef.current.scale, {
        x: 1,
        y: 1,
        z: 1,
        duration: 0.4,
        ease: 'back.out(1.5)',
      });
    }

    return () => {
      pulseRef.current?.kill();
    };
  }, [thinking]);

  // "Thought flash" — briefly spike renderer exposure by 20% when bot responds
  useEffect(() => {
    if (flashCount === 0) return;

    flashTlRef.current?.kill();

    const BASE = 1.1;
    const PEAK = BASE * 1.2; // +20%

    flashTlRef.current = gsap.timeline()
      .to(gl, {
        toneMappingExposure: PEAK,
        duration: 0.14,
        ease: 'power2.out',
      })
      .to(gl, {
        toneMappingExposure: BASE,
        duration: 0.72,
        ease: 'power3.in',
      });

    // Subtle scale micro-burst on the sphere itself
    if (meshRef.current) {
      gsap.timeline()
        .to(meshRef.current.scale, {
          x: 1.06, y: 1.06, z: 1.06,
          duration: 0.14,
          ease: 'power2.out',
        })
        .to(meshRef.current.scale, {
          x: 1, y: 1, z: 1,
          duration: 0.55,
          ease: 'elastic.out(1, 0.5)',
        });
    }

    return () => { flashTlRef.current?.kill(); };
  }, [flashCount, gl]);

  useFrame((_, delta) => {
    if (!meshRef.current) return;
    const state = getScrollMorphState();

    // Gentle idle rotation + scroll-driven rotation
    meshRef.current.rotation.y += delta * 0.15 + state.rotationY * delta;
    meshRef.current.rotation.x += delta * 0.06;

    // Scroll-driven vertical position
    meshRef.current.position.y +=
      (state.positionY - meshRef.current.position.y) * 0.06;

    // Roughness driven by thinking OR scroll
    if (matRef.current) {
      const targetRoughness = thinking ? 0.42 : state.roughness;
      matRef.current.roughness +=
        (targetRoughness - matRef.current.roughness) * 0.05;

      // Distortion breathes slightly when thinking
      const targetDistortion = thinking ? 0.7 : 0.4;
      matRef.current.distortion +=
        (targetDistortion - matRef.current.distortion) * 0.04;
    }
  });

  return (
    <mesh ref={meshRef} castShadow>
      <sphereGeometry args={[1.15, 80, 80]} />
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <MeshTransmissionMaterial
        ref={matRef as any}
        transmission={1}
        thickness={0.65}
        roughness={0.04}
        chromaticAberration={0.05}
        anisotropy={0.3}
        distortion={0.40}
        distortionScale={0.5}
        temporalDistortion={0.12}
        iridescence={0.4}
        iridescenceIOR={1.3}
        iridescenceThicknessRange={[100, 800]}
        color="#ffffff"
        attenuationColor="#fef3c7"
        attenuationDistance={0.5}
        samples={16}
      />
      <BakeShadows />
    </mesh>
  );
}
