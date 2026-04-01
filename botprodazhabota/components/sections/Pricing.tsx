'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/pricing.module.scss';

gsap.registerPlugin(ScrollTrigger);

const PLANS = [
  {
    name: 'Старт',
    price: '2 990',
    period: 'мес',
    desc: 'Для небольших заведений — кофейни, ларьки, одна точка',
    features: [
      'До 500 сообщений / мес',
      '1 сообщество VK',
      'Настройка под ваше меню',
      'Ответы 24/7 без участия',
      'Поддержка по почте',
    ],
    cta: 'Начать',
    highlight: false,
  },
  {
    name: 'Бизнес',
    price: '6 990',
    period: 'мес',
    desc: 'Для активных заведений с постоянным потоком сообщений',
    features: [
      'До 5 000 сообщений / мес',
      'До 3 сообществ VK',
      'Настройка тона и стиля',
      'Приоритетная поддержка',
      'Обновление контента',
    ],
    cta: 'Выбрать',
    highlight: true,
  },
  {
    name: 'Сеть',
    price: 'По запросу',
    period: '',
    desc: 'Для сетей, франшиз и нескольких точек',
    features: [
      'Безлимитные сообщения',
      'Неограниченно сообществ',
      'Персональная настройка',
      'Выделенный менеджер',
      'SLA 99.9% uptime',
    ],
    cta: 'Связаться',
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
              key={plan.name}
              ref={el => { if (el) cardsRef.current[i] = el; }}
              className={`${styles.card} ${plan.highlight ? styles.featured : ''}`}
            >
              {plan.highlight && <div className={styles.badge}>Популярный</div>}

              <div className={styles.top}>
                <p className={styles.planName}>{plan.name}</p>
                <div className={styles.priceRow}>
                  <span className={styles.price}>{plan.price}</span>
                  {plan.period && <span className={styles.period}>/ {plan.period}</span>}
                </div>
                <p className={styles.planDesc}>{plan.desc}</p>
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
