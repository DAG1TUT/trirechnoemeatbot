'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/shineheading.module.scss';

gsap.registerPlugin(ScrollTrigger);

interface ShineHeadingProps {
  as?: 'h1' | 'h2' | 'h3';
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export default function ShineHeading({
  as: Tag = 'h2',
  children,
  className = '',
  delay = 0,
}: ShineHeadingProps) {
  const ref = useRef<HTMLHeadingElement>(null);
  const shineRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!ref.current || !shineRef.current) return;

    // Entrance: fade up
    gsap.fromTo(
      ref.current,
      { opacity: 0, y: 30 },
      {
        opacity: 1,
        y: 0,
        duration: 1,
        delay,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: ref.current,
          start: 'top 85%',
          once: true,
        },
      }
    );

    // Shine sweep
    gsap.fromTo(
      shineRef.current,
      { x: '-110%' },
      {
        x: '160%',
        duration: 1.1,
        delay: delay + 0.3,
        ease: 'power2.inOut',
        scrollTrigger: {
          trigger: ref.current,
          start: 'top 85%',
          once: true,
        },
      }
    );
  }, [delay]);

  return (
    <Tag ref={ref} className={`${styles.heading} ${className}`}>
      {children}
      <span ref={shineRef} className={styles.shine} aria-hidden="true" />
    </Tag>
  );
}
