'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/pricing.module.scss';

gsap.registerPlugin(ScrollTrigger);

const PLANS = [
  {
    price: '3 500',
    billing: '10 500 ₽ / 3 месяца',
    sub: null,
    cta: 'Выбрать',
    highlight: false,
  },
  {
    price: '3 000',
    billing: '18 000 ₽ / полгода',
    sub: '≈ 99 ₽ в день',
    cta: 'Выбрать',
    highlight: true,
  },
];

export default function Pricing() {
  const cardsRef = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    cardsRef.current.forEach((card, i) => {
      if (!card) return;
      gsap.fromTo(card,
        { opacity: 0, y: 36, filter: 'blur(4px)' },
        { opacity: 1, y: 0, filter: 'blur(0px)', duration: .72, delay: i * .12, ease: 'power3.out',
          scrollTrigger: { trigger: card, start: 'top 88%', once: true } }
      );
    });
  }, []);

  return (
    <section id="pricing" className={styles.section}>
      <div className={styles.inner}>
        <div className={styles.heading}>
          <p className={styles.eyebrow}>Тарифы</p>
          <h2 className={styles.title}>Прозрачные цены<br />без скрытых платежей</h2>
          <p className={styles.desc}>Выберите тариф — первые 7 дней бесплатно на любом плане.</p>
        </div>

        <div className={styles.grid}>
          {PLANS.map((plan, i) => (
            <div
              key={i}
              ref={el => { if (el) cardsRef.current[i] = el; }}
              className={`${styles.card} ${plan.highlight ? styles.featured : ''}`}
            >
              <div className={styles.badgeSlot}>
                {plan.highlight && (
                  <div className={styles.badge}>⭐ Популярный</div>
                )}
              </div>

              <div className={styles.priceBlock}>
                <div className={styles.priceRow}>
                  <span className={styles.price}>{plan.price}</span>
                  <span className={styles.currency}>₽</span>
                  <span className={styles.period}>/ мес</span>
                </div>
                <p className={styles.billing}>{plan.billing}</p>
                {plan.sub && <p className={styles.sub}>{plan.sub}</p>}
              </div>

              <a href="#cta" className={`${styles.cta} ${plan.highlight ? styles.ctaFeatured : ''}`}
                onClick={e => { e.preventDefault(); document.getElementById('cta')?.scrollIntoView({ behavior: 'smooth' }); }}>
                {plan.cta}
              </a>
            </div>
          ))}
        </div>

        <div className={styles.trial}>
          <span className={styles.trialIcon}>🎁</span>
          <div>
            <p className={styles.trialTitle}>7 дней бесплатно на любом тарифе</p>
            <p className={styles.trialDesc}>Подключите бота к своему VK-сообществу и протестируйте на реальных клиентах. Карта не нужна — просто попробуйте.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
