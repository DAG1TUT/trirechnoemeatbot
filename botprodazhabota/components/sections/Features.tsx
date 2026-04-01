'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/features.module.scss';

gsap.registerPlugin(ScrollTrigger);

const FEATURES = [
  {
    icon: <svg viewBox="0 0 24 24" fill="none" width={26} height={26}><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" strokeWidth={1.5} strokeLinejoin="round"/></svg>,
    title: 'Мгновенные ответы',
    desc: 'Клиент написал — бот ответил за секунду. Днём, ночью, в праздники. Вы не пропустите ни одного сообщения.',
    stat: '< 1с', label: 'Время ответа',
  },
  {
    icon: <svg viewBox="0 0 24 24" fill="none" width={26} height={26}><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={1.5}/><path d="M12 6v6l4 2" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round"/></svg>,
    title: 'Работает 24/7',
    desc: 'Бот никогда не устаёт и не уходит на обед. Отвечает в любое время — без вашего участия.',
    stat: '24/7', label: 'Без выходных',
  },
  {
    icon: <svg viewBox="0 0 24 24" fill="none" width={26} height={26}><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke="currentColor" strokeWidth={1.5} strokeLinejoin="round"/></svg>,
    title: 'Понимает вопросы',
    desc: 'Бот читает сообщение целиком и отвечает по смыслу — как живой консультант, а не шаблонные ответы.',
    stat: 'GPT-4o', label: 'Нейросеть',
  },
  {
    icon: <svg viewBox="0 0 24 24" fill="none" width={26} height={26}><path d="M12 2a5 5 0 100 10A5 5 0 0012 2zM5 20a7 7 0 0114 0" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round"/></svg>,
    title: 'Знает ваше меню',
    desc: 'Расскажите боту о вашем заведении — он запомнит состав блюд, цены, условия доставки и ответит клиентам точно.',
    stat: '100%', label: 'Точность',
  },
  {
    icon: <svg viewBox="0 0 24 24" fill="none" width={26} height={26}><rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" strokeWidth={1.5}/><path d="M3 9h18M9 21V9" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round"/></svg>,
    title: 'Настройка за 15 минут',
    desc: 'Без кода и технических знаний. Опишите ваш бизнес — и бот готов к работе прямо сегодня.',
    stat: '15 мин', label: 'Запуск',
  },
  {
    icon: <svg viewBox="0 0 24 24" fill="none" width={26} height={26}><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" stroke="currentColor" strokeWidth={1.5} strokeLinejoin="round"/></svg>,
    title: 'Вежливый и дружелюбный',
    desc: 'Тон общения настраивается под вас: строгий, тёплый или неформальный. Бот — лицо вашего заведения.',
    stat: '∞', label: 'Терпение',
  },
];

export default function Features() {
  const cardsRef = useRef<HTMLDivElement[]>([]);

  useEffect(() => {
    cardsRef.current.forEach((card, i) => {
      if (!card) return;
      gsap.fromTo(card,
        { opacity: 0, y: 32, filter: 'blur(3px)' },
        { opacity: 1, y: 0, filter: 'blur(0px)', duration: .7, delay: i * .09, ease: 'power3.out',
          scrollTrigger: { trigger: card, start: 'top 88%', once: true } }
      );
      const onMove = (e: MouseEvent) => {
        const r = card.getBoundingClientRect();
        gsap.to(card, { rotateX: -((e.clientY - r.top) / r.height - .5) * 8,
          rotateY: ((e.clientX - r.left) / r.width - .5) * 8,
          transformPerspective: 700, duration: .35, ease: 'power1.out' });
      };
      const onLeave = () => gsap.to(card, { rotateX: 0, rotateY: 0, duration: .4, ease: 'back.out(1.5)' });
      card.addEventListener('mousemove', onMove);
      card.addEventListener('mouseleave', onLeave);
    });
  }, []);

  return (
    <section id="features" className={styles.section}>
      <div className={styles.inner}>
        <div className={styles.heading}>
          <p className={styles.eyebrow}>О сервисе</p>
          <h2 className={styles.title}>Бот, который отвечает<br />вместо вас</h2>
          <p className={styles.subdesc}>Подключите к вашему VK-сообществу — и больше не пропускайте ни одного клиента</p>
        </div>
        <div className={styles.grid}>
          {FEATURES.map((f, i) => (
            <div key={f.title} ref={el => { if (el) cardsRef.current[i] = el; }} className={styles.card}>
              <div className={styles.icon}>{f.icon}</div>
              <h3 className={styles.cardTitle}>{f.title}</h3>
              <p className={styles.cardDesc}>{f.desc}</p>
              <div className={styles.stat}>
                <span className={styles.statNum}>{f.stat}</span>
                <span className={styles.statLabel}>{f.label}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
