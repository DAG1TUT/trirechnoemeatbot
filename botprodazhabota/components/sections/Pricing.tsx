'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/pricing.module.scss';

gsap.registerPlugin(ScrollTrigger);

const PLANS: Array<{
  price: string;
  period: string;
  billing: string | null;
  features: string[];
  cta: string;
  highlight: boolean;
}> = [
  {
    price: '5 000',
    period: '/ мес',
    billing: null,
    features: [
      'Подключение к VK сообществу',
      'Настройка под ваше меню',
      'Ответы 24/7 без участия',
      'Поддержка по почте',
    ],
    cta: 'Начать',
    highlight: false,
  },
  {
    price: '3 000',
    period: '/ мес',
    billing: '18 000 ₽ раз в 6 месяцев',
    features: [
      'Подключение к VK сообществу',
      'Настройка под ваше меню',
      'Ответы 24/7 без участия',
      'Приоритетная поддержка',
    ],
    cta: 'Выбрать',
    highlight: true,
  },
  {
    price: '2 000',
    period: '/ мес',
    billing: '24 000 ₽ раз в год',
    features: [
      'Подключение к VK сообществу',
      'Настройка под ваше меню',
      'Ответы 24/7 без участия',
      'Персональная настройка',
    ],
    cta: 'Выбрать',
    highlight: false,
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
          <p className={styles.desc}>14 дней бесплатно на любом тарифе. Карта не нужна.</p>
        </div>

        <div className={styles.grid}>
          {PLANS.map((plan, i) => (
            <div
              key={i}
              ref={el => { if (el) cardsRef.current[i] = el; }}
              className={`${styles.card} ${plan.highlight ? styles.featured : ''}`}
            >
              <div className={styles.top}>
                {plan.highlight && (
                  <div className={styles.badge}>⭐ Популярный</div>
                )}
                <div className={styles.priceRow}>
                  <span className={styles.price}>{plan.price} ₽</span>
                  <span className={styles.period}>{plan.period}</span>
                </div>
                {plan.billing && (
                  <p className={styles.billing}>{plan.billing}</p>
                )}
              </div>

              <ul className={styles.features}>
                {plan.features.map(f => (
                  <li key={f} className={styles.feature}>
                    <span className={styles.check}>✓</span> {f}
                  </li>
                ))}
              </ul>

              <a href="#cta" className={`${styles.cta} ${plan.highlight ? styles.ctaFeatured : ''}`}
                onClick={e => { e.preventDefault(); document.getElementById('cta')?.scrollIntoView({ behavior: 'smooth' }); }}>
                {plan.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
