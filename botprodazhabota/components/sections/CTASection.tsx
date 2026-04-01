'use client';

import { useRef, useEffect, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/cta.module.scss';

gsap.registerPlugin(ScrollTrigger);

type State = 'idle' | 'loading' | 'success' | 'error';

export default function CTASection() {
  const sectionRef = useRef<HTMLElement>(null);
  const [state, setState] = useState<State>('idle');
  const [form, setForm] = useState({ name: '', phone: '', email: '' });

  useEffect(() => {
    if (!sectionRef.current) return;
    gsap.fromTo(
      sectionRef.current.querySelectorAll('[data-reveal]'),
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.8, stagger: 0.12, ease: 'power3.out',
        scrollTrigger: { trigger: sectionRef.current, start: 'top 80%', once: true } }
    );
  }, []);

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(p => ({ ...p, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || (!form.phone.trim() && !form.email.trim())) return;

    setState('loading');
    try {
      const res = await fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name:  form.name,
          phone: form.phone,
          email: form.email,
        }),
      });
      setState(res.ok ? 'success' : 'error');
    } catch {
      setState('error');
    }
  };

  return (
    <section ref={sectionRef} className={styles.section} id="cta">
      <div className={styles.panel}>
        <div className={styles.orb} aria-hidden="true" />

        <p data-reveal className={styles.eyebrow}>Начать бесплатно</p>

        <h2 data-reveal className={styles.title}>
          Клиенты пишут —<br />бот уже отвечает
        </h2>

        <p data-reveal className={styles.desc}>
          Оставьте заявку — подключим бота к вашему VK-сообществу и настроим под ваше меню.
          14 дней бесплатно.
        </p>

        {state === 'success' ? (
          <div data-reveal className={styles.success}>
            <svg viewBox="0 0 24 24" fill="none" width={20} height={20}>
              <path d="M5 12l5 5L19 7" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Заявка принята! Мы напишем вам в ближайшее время.
          </div>
        ) : (
          <form data-reveal onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.fieldRow}>
              <input
                type="text"
                className={styles.emailInput}
                placeholder="Ваше имя *"
                value={form.name}
                onChange={set('name')}
                required
                disabled={state === 'loading'}
              />
              <input
                type="tel"
                className={styles.emailInput}
                placeholder="Телефон"
                value={form.phone}
                onChange={set('phone')}
                disabled={state === 'loading'}
              />
            </div>
            <div className={styles.fieldRow}>
              <input
                type="email"
                className={styles.emailInput}
                placeholder="Email"
                value={form.email}
                onChange={set('email')}
                disabled={state === 'loading'}
              />
              <button
                type="submit"
                className={styles.btn}
                disabled={state === 'loading' || (!form.name.trim() || (!form.phone.trim() && !form.email.trim()))}
              >
                {state === 'loading' ? (
                  <span className={styles.spinner} />
                ) : (
                  <>
                    Получить доступ
                    <svg viewBox="0 0 16 16" fill="none" width={14} height={14}>
                      <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </>
                )}
              </button>
            </div>

            {state === 'error' && (
              <p className={styles.errorMsg}>Ошибка отправки. Попробуйте ещё раз.</p>
            )}
          </form>
        )}

        <p data-reveal className={styles.note}>
          Без кредитной карты · Отмена в любой момент
        </p>

        <div data-reveal className={styles.badges}>
          <div className={styles.badge}>
            <svg viewBox="0 0 24 24" fill="none" width={14} height={14}>
              <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z" fill="currentColor"/>
            </svg>
            4.9 / 5 — 200+ клиентов
          </div>
          <div className={styles.badge}>
            <svg viewBox="0 0 24 24" fill="none" width={14} height={14}>
              <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth={1.5}/>
              <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round"/>
            </svg>
            Безопасное подключение
          </div>
        </div>
      </div>
    </section>
  );
}
