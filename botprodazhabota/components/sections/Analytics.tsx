'use client';

import { useRef, useEffect, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '@/styles/analytics.module.scss';

gsap.registerPlugin(ScrollTrigger);

/* ── Mock data ────────────────────────────────────────────────────── */
const DAYS = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'];
const MSGS = [38, 52, 47, 71, 85, 112, 94];
const ORDERS = [6, 9, 8, 14, 17, 22, 18];

const TOP_Q = [
  { q: 'Время доставки',    pct: 82, n: 143 },
  { q: 'Состав роллов',     pct: 67, n: 117 },
  { q: 'Минимальный заказ', pct: 54, n:  94 },
  { q: 'Акции и скидки',    pct: 41, n:  71 },
  { q: 'Оплата картой',     pct: 29, n:  51 },
];

const FUNNEL = [
  { label: 'Написали',    n: 519, pct: 100 },
  { label: 'Получили ответ', n: 519, pct: 100 },
  { label: 'Спросили цену', n: 312, pct: 60 },
  { label: 'Оформили заказ', n: 94, pct: 18 },
];

const RECENT = [
  { time: '14:32', text: 'Можно ли заказать без лука?',      status: 'answered' },
  { time: '14:28', text: 'Сколько везут по адресу Ленина 12?', status: 'answered' },
  { time: '14:21', text: 'Есть ли детское меню?',            status: 'answered' },
  { time: '14:15', text: 'Принимаете карты мир?',            status: 'answered' },
  { time: '14:09', text: 'Как отследить заказ?',             status: 'lead' },
];

const MAX_MSGS = Math.max(...MSGS);
const MAX_ORD  = Math.max(...ORDERS);

/* ── Bar chart component ─────────────────────────────────────────── */
function Bar({ pct, value, accent, delay }: { pct: number; value: number; accent?: boolean; delay: number }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    gsap.fromTo(ref.current,
      { scaleY: 0 },
      { scaleY: 1, duration: .6, delay, ease: 'power3.out',
        scrollTrigger: { trigger: ref.current, start: 'top 92%', once: true } }
    );
  }, [delay]);
  return (
    <div className={styles.barWrap}>
      <div ref={ref} className={`${styles.bar} ${accent ? styles.barAccent : ''}`}
        style={{ height: `${Math.max(pct * 140 / 100, 6)}px`, transformOrigin: 'bottom' }} />
      <span className={styles.barVal}>{value}</span>
    </div>
  );
}

/* ── Animated counter ────────────────────────────────────────────── */
function Counter({ to, suffix = '' }: { to: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    ScrollTrigger.create({
      trigger: ref.current, start: 'top 88%', once: true,
      onEnter() {
        const proxy = { v: 0 };
        gsap.to(proxy, { v: to, duration: 1.2, ease: 'power2.out',
          onUpdate() { setVal(Math.round(proxy.v)); } });
      },
    });
  }, [to]);
  return <span ref={ref}>{val.toLocaleString('ru')}{suffix}</span>;
}

export default function Analytics() {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;
    gsap.fromTo(sectionRef.current.querySelectorAll('[data-fade]'),
      { opacity: 0, y: 28 },
      { opacity: 1, y: 0, duration: .7, stagger: .1, ease: 'power3.out',
        scrollTrigger: { trigger: sectionRef.current, start: 'top 80%', once: true } }
    );
  }, []);

  return (
    <section id="analytics" ref={sectionRef} className={styles.section}>
      <div className={styles.inner}>

        {/* Heading */}
        <div data-fade className={styles.heading}>
          <p className={styles.eyebrow}>Аналитика</p>
          <h2 className={styles.title}>Всё в одном дашборде</h2>
          <p className={styles.desc}>
            Видите обращения, популярные вопросы и конверсию в заказ — в реальном времени.
          </p>
        </div>

        {/* KPI row */}
        <div data-fade className={styles.kpiRow}>
          {[
            { label: 'Сообщений за неделю', val: 499, suffix: '' },
            { label: 'Заказов оформлено',   val: 94,  suffix: '' },
            { label: 'Конверсия в заказ',   val: 18,  suffix: '%' },
            { label: 'Ср. время ответа',    val: 0.8, suffix: 'с' },
          ].map(k => (
            <div key={k.label} className={styles.kpi}>
              <span className={styles.kpiNum}>
                {k.val === 0.8 ? '< 1' : <Counter to={k.val} suffix={k.suffix} />}
                {k.val === 0.8 ? 'с' : ''}
              </span>
              <span className={styles.kpiLabel}>{k.label}</span>
            </div>
          ))}
        </div>

        {/* Main dashboard card */}
        <div data-fade className={styles.dashboard}>

          {/* Left: charts */}
          <div className={styles.left}>
            <div className={styles.chartCard}>
              <div className={styles.chartHeader}>
                <span className={styles.chartTitle}>Сообщения / Заказы — 7 дней</span>
                <div className={styles.legend}>
                  <span className={styles.legDot} />Сообщения
                  <span className={`${styles.legDot} ${styles.legAccent}`} />Заказы
                </div>
              </div>
              <div className={styles.chartArea}>
                <div className={styles.bars}>
                  {DAYS.map((d, i) => (
                    <div key={d} className={styles.barGroup}>
                      <Bar pct={Math.round(MSGS[i] / MAX_MSGS * 100)} value={MSGS[i]} delay={i * .06} />
                      <Bar pct={Math.round(ORDERS[i] / MAX_ORD * 100)} value={ORDERS[i]} accent delay={i * .06 + .04} />
                      <span className={styles.barLabel}>{d}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Top questions */}
            <div className={styles.chartCard}>
              <p className={styles.chartTitle}>Топ вопросов</p>
              <div className={styles.topList}>
                {TOP_Q.map((q, i) => (
                  <div key={q.q} className={styles.topItem}>
                    <div className={styles.topMeta}>
                      <span className={styles.topQ}>{q.q}</span>
                      <span className={styles.topN}>{q.n}</span>
                    </div>
                    <div className={styles.progressTrack}>
                      <div className={styles.progressFill}
                        style={{ '--pct': `${q.pct}%`, animationDelay: `${i * .1 + .3}s` } as React.CSSProperties} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: funnel + feed */}
          <div className={styles.right}>
            {/* Funnel */}
            <div className={styles.chartCard}>
              <p className={styles.chartTitle}>Воронка продаж</p>
              <div className={styles.funnel}>
                {FUNNEL.map((f, i) => (
                  <div key={f.label} className={styles.funnelStep}>
                    <div className={styles.funnelBar}
                      style={{ width: `${f.pct}%`, animationDelay: `${i * .12 + .2}s` } as React.CSSProperties}>
                      <span className={styles.funnelN}>{f.n}</span>
                    </div>
                    <span className={styles.funnelLabel}>{f.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent messages */}
            <div className={styles.chartCard}>
              <p className={styles.chartTitle}>Последние обращения</p>
              <div className={styles.feed}>
                {RECENT.map((r, i) => (
                  <div key={i} className={styles.feedItem}>
                    <span className={styles.feedTime}>{r.time}</span>
                    <span className={styles.feedText}>{r.text}</span>
                    <span className={`${styles.feedTag} ${r.status === 'lead' ? styles.feedLead : ''}`}>
                      {r.status === 'lead' ? 'Лид' : '✓'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
