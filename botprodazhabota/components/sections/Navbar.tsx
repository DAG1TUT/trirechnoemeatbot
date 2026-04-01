'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/navbar.module.scss';

gsap.registerPlugin(ScrollTrigger);

const VKLogo = () => (
  <svg width="34" height="34" viewBox="0 0 34 34" fill="none">
    <rect width="34" height="34" rx="9" fill="#3D6FBB"/>
    <path d="M18.3 23.5c-6.6 0-10.4-4.5-10.5-12h3.3c.1 5.5 2.5 7.8 4.4 8.3V11.5H18.8v4.7c1.9-.2 3.9-2.4 4.6-4.7h3.1c-.5 3-2.6 5.1-4.1 6 1.5.7 3.9 2.6 4.8 6h-3.4c-.7-2.2-2.5-4-4.9-4.2V23.5h-.6z" fill="white"/>
  </svg>
);

const LINKS = [
  { label: 'О сервисе', href: '#features' },
  { label: 'Настройка', href: '#configure' },
  { label: 'Тарифы',    href: '#pricing' },
  { label: 'Демо',      href: '#demo' },
];

export default function Navbar() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    gsap.fromTo(ref.current, { opacity: 0, y: -18 }, { opacity: 1, y: 0, duration: .65, delay: .1, ease: 'power3.out' });

    ScrollTrigger.create({
      start: 'top -50px',
      onUpdate(self) {
        if (!ref.current) return;
        self.scroll() > 50
          ? ref.current.setAttribute('data-s', '')
          : ref.current.removeAttribute('data-s');
      },
    });
  }, []);

  const go = (href: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    document.getElementById(href.replace('#', ''))?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <nav ref={ref} className={styles.nav}>
      <a href="#demo" className={styles.brand} onClick={go('#demo')}>
        <VKLogo />
      </a>

      <div className={styles.links}>
        {LINKS.map(l => (
          <a key={l.href} href={l.href} onClick={go(l.href)}>{l.label}</a>
        ))}
      </div>

      <a href="#pricing" className={styles.cta} onClick={go('#pricing')}>
        Подключить бота
      </a>
    </nav>
  );
}
