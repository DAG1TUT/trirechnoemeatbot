'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import styles from '@/styles/splitreveal.module.scss';

interface SplitRevealProps {
  text: string;
  onComplete?: () => void;
}

export default function SplitReveal({ text, onComplete }: SplitRevealProps) {
  const containerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const spans = containerRef.current.querySelectorAll<HTMLSpanElement>('.' + styles.char);
    if (!spans.length) return;

    const tl = gsap.timeline({ onComplete });

    tl.fromTo(
      spans,
      {
        opacity: 0,
        filter: 'blur(6px)',
        y: 4,
      },
      {
        opacity: 1,
        filter: 'blur(0px)',
        y: 0,
        duration: 0.35,
        stagger: 0.018,
        ease: 'power2.out',
      }
    );

    return () => { tl.kill(); };
  }, [text, onComplete]);

  return (
    <span ref={containerRef} className={styles.wrapper}>
      {text.split('').map((char, i) => (
        <span
          key={i}
          className={styles.char}
          style={{ display: char === ' ' ? 'inline' : 'inline-block' }}
        >
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </span>
  );
}
