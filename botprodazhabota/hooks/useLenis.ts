'use client';

import { useEffect, useRef } from 'react';
import Lenis from 'lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

let lenisInstance: Lenis | null = null;

export function getLenis() {
  return lenisInstance;
}

export function useLenis() {
  // Store the RAF function in a ref so we can cleanly remove it from the ticker
  const rafFnRef = useRef<((time: number) => void) | null>(null);

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.0,
      easing: (t) => 1 - Math.pow(1 - t, 3), // cubic ease-out — lighter than exponential
      orientation: 'vertical',
      smoothWheel: true,
      touchMultiplier: 1.5,
    });

    lenisInstance = lenis;

    // Stable function reference so gsap.ticker.remove works correctly
    rafFnRef.current = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(rafFnRef.current);
    gsap.ticker.lagSmoothing(0);

    lenis.on('scroll', ScrollTrigger.update);

    return () => {
      if (rafFnRef.current) {
        gsap.ticker.remove(rafFnRef.current);
        rafFnRef.current = null;
      }
      lenis.off('scroll', ScrollTrigger.update);
      lenis.destroy();
      lenisInstance = null;
    };
  }, []);
}
