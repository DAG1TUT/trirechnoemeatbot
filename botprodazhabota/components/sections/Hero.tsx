'use client';

import { useRef, useEffect, useCallback } from 'react';
import gsap from 'gsap';
import GlassChat from '@/components/chat/GlassChat';
import { LeftDecorations, RightDecorations } from '@/components/ui/FloatingDecorations';
import styles from '@/styles/hero.module.scss';

export default function Hero({ systemPrompt }: { systemPrompt?: string }) {
  const headlineRef  = useRef<HTMLDivElement>(null);
  const flashRef     = useRef<HTMLDivElement>(null);
  const chatWrapRef  = useRef<HTMLDivElement>(null);

  const handleBotFlash = useCallback(() => {
    if (flashRef.current) {
      gsap.timeline()
        .set(flashRef.current,  { opacity: 0 })
        .to(flashRef.current,   { opacity: 1, duration: 0.14, ease: 'power2.out' })
        .to(flashRef.current,   { opacity: 0, duration: 0.65, ease: 'power3.in' });
    }
    if (chatWrapRef.current) {
      gsap.timeline()
        .to(chatWrapRef.current, { scale: 1.010, duration: 0.12, ease: 'power2.out' })
        .to(chatWrapRef.current, { scale: 1,     duration: 0.48, ease: 'elastic.out(1,0.5)' });
    }
  }, []);

  useEffect(() => {
    if (!headlineRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo('[data-e]', { opacity: 0, y: 20 }, {
        opacity: 1, y: 0,
        duration: 0.70, stagger: 0.09, delay: 0.15,
        ease: 'power3.out',
      });
    }, headlineRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="demo" className={styles.hero}>
      <div className={styles.content}>

        {/* Headline */}
        <div ref={headlineRef} className={styles.headlineGroup}>
          <h1 data-e className={styles.headline}>
            Бот, который отвечает<br />
            за вас в&nbsp;<span className={styles.accentWord}>VK</span>
          </h1>
          <p data-e className={styles.sub}>
            Пишут клиенты — бот отвечает · 24 / 7 · Без вашего участия
          </p>
        </div>

        {/* Hero row */}
        <div className={styles.heroRow}>
          <LeftDecorations />

          <div ref={chatWrapRef} className={styles.chatWrap}>
            <div ref={flashRef} className={styles.flashOverlay} aria-hidden="true" />
            <GlassChat onBotFlash={handleBotFlash} systemPrompt={systemPrompt} />
          </div>

          <RightDecorations />
        </div>

        {/* CTA */}
          <div data-e className={styles.ctaRow}>
          <a href="#pricing" className={styles.cta}
            onClick={(e) => { e.preventDefault(); document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' }); }}>
            Подключить бота
          </a>
          <div className={styles.ctaStats}>
            <span><strong>200+</strong> заведений</span>
            <span className={styles.divider} />
            <span><strong>&lt;1с</strong> ответ</span>
            <span className={styles.divider} />
            <span><strong>24/7</strong> онлайн</span>
          </div>
        </div>
      </div>

      <div className={styles.scrollHint} aria-hidden="true">
        <span className={styles.scrollLine} />
      </div>
    </section>
  );
}
