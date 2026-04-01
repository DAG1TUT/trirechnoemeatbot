'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import ShineHeading from '@/components/ui/ShineHeading';
import styles from '@/styles/howitworks.module.scss';

gsap.registerPlugin(ScrollTrigger);

const STEPS = [
  {
    num: '01',
    title: 'Подключите сообщество',
    desc: 'Авторизуйтесь через VK и выберите нужное сообщество. Блик получит права на работу с сообщениями.',
  },
  {
    num: '02',
    title: 'Выберите шаблон воронки',
    desc: 'Готовые сценарии для продаж, консультаций и поддержки. Или создайте свою воронку с нуля.',
  },
  {
    num: '03',
    title: 'Обучите AI под ваш бизнес',
    desc: 'Загрузите информацию о продуктах, ценах и FAQ. Блик запомнит всё и будет отвечать точно.',
  },
  {
    num: '04',
    title: 'Запустите и зарабатывайте',
    desc: 'Включите бота одним кликом. Следите за лидами в реальном времени, пока Блик работает за вас.',
  },
];

export default function HowItWorks() {
  const lineRef = useRef<HTMLDivElement>(null);
  const stepsRef = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    // Animate the connecting line
    if (lineRef.current) {
      gsap.fromTo(
        lineRef.current,
        { scaleX: 0 },
        {
          scaleX: 1,
          transformOrigin: 'left center',
          duration: 1.4,
          ease: 'power2.inOut',
          scrollTrigger: {
            trigger: lineRef.current,
            start: 'top 80%',
            once: true,
          },
        }
      );
    }

    stepsRef.current.forEach((step, i) => {
      if (!step) return;
      gsap.fromTo(
        step,
        { opacity: 0, y: 30 },
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          delay: i * 0.15,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: step,
            start: 'top 85%',
            once: true,
          },
        }
      );
    });
  }, []);

  return (
    <section className={styles.section} id="how-it-works">
      <div className={styles.inner}>
        <div className={styles.heading}>
          <p className={styles.eyebrow}>Как это работает</p>
          <ShineHeading as="h2" className={styles.title}>
            Запуск за 15 минут
          </ShineHeading>
          <p className={styles.subtitle}>
            Без кода, без разработчиков. Просто настройте и включите.
          </p>
        </div>

        <div className={styles.stepsWrap}>
          <div ref={lineRef} className={styles.connectingLine} aria-hidden="true" />

          <div className={styles.steps}>
            {STEPS.map((step, i) => (
              <div
                key={step.num}
                ref={(el) => { if (el) stepsRef.current[i] = el; }}
                className={styles.step}
              >
                <div className={styles.stepNum}>{step.num}</div>
                <div className={styles.stepContent}>
                  <h3 className={styles.stepTitle}>{step.title}</h3>
                  <p className={styles.stepDesc}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
