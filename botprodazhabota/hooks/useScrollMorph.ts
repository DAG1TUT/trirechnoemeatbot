'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export interface ScrollMorphState {
  progress: number;
  rotationY: number;
  positionY: number;
  scale: number;
  roughness: number;
}

const state: ScrollMorphState = {
  progress: 0,
  rotationY: 0,
  positionY: 0,
  scale: 1,
  roughness: 0.04,
};

export function getScrollMorphState() {
  return state;
}

export function useScrollMorph(triggerSelector = '#hero') {
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: triggerSelector,
        start: 'top top',
        end: 'bottom top',
        scrub: 1.5,
        onUpdate: (self) => {
          state.progress = self.progress;
        },
      },
    });

    tl.to(state, {
      rotationY: Math.PI * 2.5,
      positionY: -1.2,
      scale: 0.75,
      roughness: 0.28,
      ease: 'none',
    });

    return () => {
      tl.kill();
      initialized.current = false;
    };
  }, [triggerSelector]);
}
