'use client';

import { useState, useEffect, useCallback } from 'react';
import styles from './admin.module.css';

interface Client {
  id: string;
  apiKey: string;
  businessName: string;
  businessType: string | null;
  systemPrompt: string;
  isActive: boolean;
  createdAt: string;
}

const BUSINESS_TYPES = [
  'Суши / Роллы', 'Пицца', 'Доставка еды', 'Кафе / Кофейня',
  'Бургерная', 'Шаурма / Фастфуд', 'Мясной ресторан', 'Пекарня', 'Другое',
];

export default function AdminPage() {
  const [secret, setSecret]     = useState('');
  const [authed, setAuthed]     = useState(false);
  const [clients, setClients]   = useState<Client[]>([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [copied, setCopied]     = useState('');
  const [editing, setEditing]   = useState<Client | null>(null);

  const [form, setForm] = useState({
    businessName: '', businessType: '', systemPrompt: '',
  });

  const headers = useCallback(() => ({
    'Content-Type': 'application/json',
    'x-admin-secret': secret,
  }), [secret]);

  const load = useCallback(async () => {
    setLoading(true);
    const res = await fetch('/api/client', { headers: headers() });
    if (res.status === 401) { setError('Неверный пароль'); setAuthed(false); }
    else { setClients(await res.json()); setError(''); }
    setLoading(false);
  }, [headers]);

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthed(true);
    await load();
  };

  useEffect(() => { if (authed) load(); }, [authed, load]);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.businessName || !form.systemPrompt) return;
    await fetch('/api/client', {
      method: 'POST', headers: headers(),
      body: JSON.stringify(form),
    });
    setForm({ businessName: '', businessType: '', systemPrompt: '' });
    load();
  };

  const save = async () => {
    if (!editing) return;
    await fetch(`/api/client/${editing.apiKey}`, {
      method: 'PATCH', headers: headers(),
      body: JSON.stringify({
        businessName: editing.businessName,
        businessType: editing.businessType,
        systemPrompt: editing.systemPrompt,
        isActive: editing.isActive,
      }),
    });
    setEditing(null);
    load();
  };

  const toggle = async (c: Client) => {
    await fetch(`/api/client/${c.apiKey}`, {
      method: 'PATCH', headers: headers(),
      body: JSON.stringify({ isActive: !c.isActive }),
    });
    load();
  };

  const copy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(''), 1800);
  };

  if (!authed) return (
    <div className={styles.login}>
      <h1>Блик — Админка</h1>
      <form onSubmit={login}>
        <input type="password" placeholder="Пароль (ADMIN_SECRET)"
          value={secret} onChange={e => setSecret(e.target.value)} />
        <button type="submit">Войти</button>
        {error && <p className={styles.err}>{error}</p>}
      </form>
    </div>
  );

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1>Клиенты Блик</h1>
        <span className={styles.count}>{clients.length} заведений</span>
        <button className={styles.refresh} onClick={load}>↻</button>
      </header>

      {/* Create form */}
      <section className={styles.createCard}>
        <h2>Добавить клиента</h2>
        <form onSubmit={create} className={styles.createForm}>
          <input placeholder="Название заведения *" value={form.businessName}
            onChange={e => setForm(p => ({ ...p, businessName: e.target.value }))} required />
          <select value={form.businessType}
            onChange={e => setForm(p => ({ ...p, businessType: e.target.value }))}>
            <option value="">Тип (необязательно)</option>
            {BUSINESS_TYPES.map(t => <option key={t}>{t}</option>)}
          </select>
          <textarea rows={4} placeholder="Системный промт *"
            value={form.systemPrompt}
            onChange={e => setForm(p => ({ ...p, systemPrompt: e.target.value }))} required />
          <button type="submit">Создать → получить API ключ</button>
        </form>
      </section>

      {/* Client list */}
      {loading && <p className={styles.loading}>Загрузка…</p>}
      <div className={styles.grid}>
        {clients.map(c => (
          <div key={c.id} className={`${styles.card} ${!c.isActive ? styles.inactive : ''}`}>
            {editing?.id === c.id ? (
              /* Edit mode */
              <div className={styles.editMode}>
                <input value={editing.businessName}
                  onChange={e => setEditing(p => p && ({ ...p, businessName: e.target.value }))} />
                <textarea rows={5} value={editing.systemPrompt}
                  onChange={e => setEditing(p => p && ({ ...p, systemPrompt: e.target.value }))} />
                <div className={styles.editBtns}>
                  <button onClick={save} className={styles.save}>Сохранить</button>
                  <button onClick={() => setEditing(null)} className={styles.cancel}>Отмена</button>
                </div>
              </div>
            ) : (
              /* View mode */
              <>
                <div className={styles.cardHeader}>
                  <div>
                    <span className={styles.bizName}>{c.businessName}</span>
                    {c.businessType && <span className={styles.bizType}>{c.businessType}</span>}
                  </div>
                  <span className={`${styles.status} ${c.isActive ? styles.active : styles.off}`}>
                    {c.isActive ? 'Активен' : 'Отключён'}
                  </span>
                </div>

                {/* API Key */}
                <div className={styles.keyRow}>
                  <code className={styles.key}>{c.apiKey}</code>
                  <button className={styles.copyBtn}
                    onClick={() => copy(c.apiKey, c.id + 'key')}>
                    {copied === c.id + 'key' ? '✓' : 'Копировать'}
                  </button>
                </div>

                {/* Prompt preview */}
                <p className={styles.promptPreview}>{c.systemPrompt.slice(0, 120)}…</p>

                {/* Actions */}
                <div className={styles.actions}>
                  <button onClick={() => setEditing(c)}>Редактировать</button>
                  <button onClick={() => toggle(c)} className={styles.toggleBtn}>
                    {c.isActive ? 'Отключить' : 'Включить'}
                  </button>
                  <button className={styles.copyBtn}
                    onClick={() => copy(
                      `curl -X POST https://ваш-домен/api/chat \\\n  -H "Content-Type: application/json" \\\n  -d '{"message":"Привет","apiKey":"${c.apiKey}"}'`,
                      c.id + 'curl'
                    )}>
                    {copied === c.id + 'curl' ? '✓ curl скопирован' : 'Скопировать curl'}
                  </button>
                </div>

                <p className={styles.date}>
                  Создан: {new Date(c.createdAt).toLocaleDateString('ru')}
                </p>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
