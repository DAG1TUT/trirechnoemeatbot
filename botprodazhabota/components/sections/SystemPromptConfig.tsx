'use client';

import { useState } from 'react';
import styles from '@/styles/systemprompt.module.scss';

const BUSINESS_TYPES = [
  { value: 'sushi',    label: '🍱 Суши / Роллы' },
  { value: 'pizza',    label: '🍕 Пицца' },
  { value: 'delivery', label: '🛵 Доставка еды' },
  { value: 'cafe',     label: '☕ Кафе / Кофейня' },
  { value: 'burger',   label: '🍔 Бургерная' },
  { value: 'shawarma', label: '🌯 Шаурма / Фастфуд' },
  { value: 'bbq',      label: '🥩 Мясной ресторан' },
  { value: 'bakery',   label: '🥐 Пекарня / Кондитерская' },
  { value: 'other',    label: '🏪 Другое заведение' },
];

const TEMPLATE: Record<string, string> = {
  sushi:    'Ты — консультант суши-ресторана {name} в VK. Отвечай на вопросы клиентов о меню, составах роллов, аллергенах, времени доставки и часах работы. Будь дружелюбным и конкретным.',
  pizza:    'Ты — консультант пиццерии {name} в VK. Отвечай на вопросы о видах пиццы, составе, размерах, ценах и условиях доставки. Будь вежливым и helpful.',
  delivery: 'Ты — консультант службы доставки {name} в VK. Отвечай на вопросы о зоне доставки, времени, минимальном заказе и способах оплаты. Будь чётким и быстрым.',
  cafe:     'Ты — консультант кафе {name} в VK. Рассказывай о меню, напитках, десертах, часах работы и возможности бронирования. Общайся тепло и приветливо.',
  burger:   'Ты — консультант бургерной {name} в VK. Помогай с выбором бургеров, рассказывай о составе, добавках и соусах. Будь живым и дружелюбным.',
  shawarma: 'Ты — консультант {name} в VK. Рассказывай о видах шаурмы, составе, соусах и времени приготовления. Отвечай быстро и по делу.',
  bbq:      'Ты — консультант ресторана {name} в VK. Рассказывай о видах мяса, способах приготовления и гарнирах. Помогай с вопросами о бронировании.',
  bakery:   'Ты — консультант пекарни {name} в VK. Рассказывай о свежей выпечке, тортах на заказ, составе и ценах. Будь добрым и внимательным.',
  other:    'Ты — консультант заведения {name} в VK. Отвечай на вопросы клиентов о меню, ценах и режиме работы. Будь дружелюбным и полезным.',
};

interface Props {
  onApply: (prompt: string) => void;
}

export default function SystemPromptConfig({ onApply }: Props) {
  const [type,    setType]    = useState('sushi');
  const [name,    setName]    = useState('');
  const [custom,  setCustom]  = useState('');
  const [applied, setApplied] = useState(false);

  const buildPrompt = () => {
    const base = custom.trim() ||
      TEMPLATE[type].replace('{name}', name.trim() || 'нашего заведения');
    return base;
  };

  const handleApply = () => {
    const prompt = buildPrompt();
    onApply(prompt);
    setApplied(true);
    setTimeout(() => {
      document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
    }, 300);
    setTimeout(() => setApplied(false), 3000);
  };

  const autoFill = () => {
    setCustom(TEMPLATE[type].replace('{name}', name.trim() || 'нашего заведения'));
  };

  return (
    <section id="configure" className={styles.section}>
      <div className={styles.inner}>
        <div className={styles.heading}>
          <p className={styles.eyebrow}>Попробуйте прямо сейчас</p>
          <h2 className={styles.title}>
            Настройте под<br />ваше заведение
          </h2>
          <p className={styles.desc}>
            Укажите тип и название — бот сразу начнёт отвечать как консультант вашего заведения.
            Результат увидите в демо-чате выше.
          </p>
        </div>

        <div className={styles.card}>
          {/* Business type */}
          <div className={styles.field}>
            <label className={styles.label}>Тип заведения</label>
            <div className={styles.types}>
              {BUSINESS_TYPES.map(t => (
                <button
                  key={t.value}
                  className={`${styles.typeBtn} ${type === t.value ? styles.active : ''}`}
                  onClick={() => { setType(t.value); setCustom(''); }}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Business name */}
          <div className={styles.field}>
            <label className={styles.label}>Название заведения</label>
            <input
              className={styles.input}
              type="text"
              placeholder="Например: Суши Мастер, Пицца Nova, Кофе & Ко…"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>

          {/* Custom system prompt */}
          <div className={styles.field}>
            <div className={styles.labelRow}>
              <label className={styles.label}>Системный промт (необязательно)</label>
              <button className={styles.autoBtn} onClick={autoFill}>
                ✦ Сгенерировать авто
              </button>
            </div>
            <textarea
              className={styles.textarea}
              rows={4}
              placeholder="Опишите ваш бизнес, меню, правила и тон общения. Бот будет следовать этим инструкциям…"
              value={custom}
              onChange={e => setCustom(e.target.value)}
            />
          </div>

          <div className={styles.footer}>
            <button className={`${styles.applyBtn} ${applied ? styles.success : ''}`} onClick={handleApply}>
              {applied ? '✓ Применено — проверьте чат выше' : 'Применить к демо-чату ↑'}
            </button>
            <p className={styles.hint}>
              Бот обновится мгновенно. Задайте ему любой вопрос о вашем заведении.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
