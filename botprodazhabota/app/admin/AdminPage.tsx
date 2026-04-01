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
  vkGroupId: string | null;
  vkAccessToken: string | null;
  vkConfirmCode: string | null;
  vkSecretKey: string | null;
}

const BIZ_TYPES = [
  'Суши / Роллы','Пицца','Доставка еды','Кафе / Кофейня',
  'Бургерная','Шаурма / Фастфуд','Мясной ресторан','Пекарня','Другое',
];

function getWebhookUrl(groupId: string) {
  const base = typeof window !== 'undefined' ? window.location.origin : '';
  return `${base}/api/vk/${groupId}`;
}

export default function AdminPage() {
  const [secret, setSecret]   = useState('');
  const [authed, setAuthed]   = useState(false);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoad]    = useState(false);
  const [error, setError]     = useState('');
  const [copied, setCopied]   = useState('');
  const [open, setOpen]       = useState<string | null>(null); // expanded client id
  const [vkEdit, setVkEdit]   = useState<Partial<Client>>({});

  const [form, setForm] = useState({ businessName: '', businessType: '', systemPrompt: '' });

  const hdrs = useCallback(() => ({
    'Content-Type': 'application/json',
    'x-admin-secret': secret,
  }), [secret]);

  const load = useCallback(async () => {
    setLoad(true);
    const res = await fetch('/api/client', { headers: hdrs() });
    if (res.status === 401) { setError('Неверный пароль'); setAuthed(false); }
    else { setClients(await res.json()); setError(''); }
    setLoad(false);
  }, [hdrs]);

  useEffect(() => { if (authed) load(); }, [authed, load]);

  const login = async (e: React.FormEvent) => {
    e.preventDefault(); setAuthed(true); await load();
  };

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.businessName || !form.systemPrompt) return;
    await fetch('/api/client', { method: 'POST', headers: hdrs(), body: JSON.stringify(form) });
    setForm({ businessName: '', businessType: '', systemPrompt: '' });
    load();
  };

  const saveVK = async (c: Client) => {
    await fetch(`/api/client/${c.apiKey}`, {
      method: 'PATCH', headers: hdrs(),
      body: JSON.stringify(vkEdit),
    });
    setVkEdit({});
    load();
  };

  const toggle = async (c: Client) => {
    await fetch(`/api/client/${c.apiKey}`, {
      method: 'PATCH', headers: hdrs(),
      body: JSON.stringify({ isActive: !c.isActive }),
    });
    load();
  };

  const copy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopied(key); setTimeout(() => setCopied(''), 1800);
  };

  const expand = (id: string) => {
    if (open === id) { setOpen(null); setVkEdit({}); }
    else { setOpen(id); const c = clients.find(x => x.id === id)!;
      setVkEdit({ vkGroupId: c.vkGroupId ?? '', vkConfirmCode: c.vkConfirmCode ?? '',
                  vkSecretKey: c.vkSecretKey ?? '', vkAccessToken: c.vkAccessToken ?? '' }); }
  };

  if (!authed) return (
    <div className={styles.login}>
      <div className={styles.loginBox}>
        <div className={styles.logo}>⚡ Блик Админ</div>
        <form onSubmit={login}>
          <input type="password" placeholder="Пароль (ADMIN_SECRET)"
            value={secret} onChange={e => setSecret(e.target.value)} autoFocus />
          <button type="submit">Войти</button>
          {error && <p className={styles.err}>{error}</p>}
        </form>
      </div>
    </div>
  );

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo}>⚡ Блик</span>
          <span className={styles.count}>{clients.length} клиентов</span>
        </div>
        <button className={styles.refresh} onClick={load}>↻ Обновить</button>
      </header>

      {/* Create new client */}
      <section className={styles.createCard}>
        <h2>+ Новый клиент</h2>
        <form onSubmit={create} className={styles.createForm}>
          <input placeholder="Название заведения *" value={form.businessName}
            onChange={e => setForm(p => ({ ...p, businessName: e.target.value }))} required />
          <select value={form.businessType}
            onChange={e => setForm(p => ({ ...p, businessType: e.target.value }))}>
            <option value="">Тип заведения</option>
            {BIZ_TYPES.map(t => <option key={t}>{t}</option>)}
          </select>
          <textarea rows={4} placeholder="Системный промт — опишите заведение, меню, тон общения *"
            value={form.systemPrompt}
            onChange={e => setForm(p => ({ ...p, systemPrompt: e.target.value }))} required />
          <button type="submit">Создать клиента →</button>
        </form>
      </section>

      {loading && <p className={styles.loading}>Загрузка…</p>}

      {/* Client list */}
      <div className={styles.list}>
        {clients.map(c => (
          <div key={c.id} className={`${styles.clientCard} ${!c.isActive ? styles.inactive : ''}`}>

            {/* Client header row */}
            <div className={styles.clientHeader}>
              <div className={styles.clientInfo}>
                <span className={styles.bizName}>{c.businessName}</span>
                {c.businessType && <span className={styles.bizType}>{c.businessType}</span>}
                <span className={`${styles.badge} ${c.vkGroupId ? styles.badgeGreen : styles.badgeGray}`}>
                  {c.vkGroupId ? '✓ VK подключён' : '○ VK не настроен'}
                </span>
              </div>
              <div className={styles.clientActions}>
                <span className={`${styles.status} ${c.isActive ? styles.active : styles.off}`}>
                  {c.isActive ? 'Активен' : 'Откл.'}
                </span>
                <button onClick={() => expand(c.id)} className={styles.settingsBtn}>
                  {open === c.id ? '▲ Закрыть' : '⚙ Настройки'}
                </button>
                <button onClick={() => toggle(c)} className={styles.toggleBtn}>
                  {c.isActive ? 'Отключить' : 'Включить'}
                </button>
              </div>
            </div>

            {/* Expanded: VK setup */}
            {open === c.id && (
              <div className={styles.vkSetup}>

                {/* Step 1 */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>1</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Откройте управление сообществом VK</p>
                    <p className={styles.stepDesc}>
                      VK → Ваше сообщество → <b>Управление</b> → <b>Работа с API</b> → <b>Callback API</b>
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>2</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Введите ID вашего сообщества</p>
                    <p className={styles.stepDesc}>
                      Найдите в адресной строке: vk.com/club<b>123456789</b> — это и есть ID
                    </p>
                    <input className={styles.vkInput} placeholder="Например: 123456789"
                      value={vkEdit.vkGroupId ?? ''}
                      onChange={e => setVkEdit(p => ({ ...p, vkGroupId: e.target.value }))} />
                  </div>
                </div>

                {/* Step 3: Webhook URL */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>3</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Вставьте этот URL в поле «Адрес сервера» VK</p>
                    <div className={styles.urlRow}>
                      <code className={styles.urlBox}>
                        {vkEdit.vkGroupId
                          ? getWebhookUrl(vkEdit.vkGroupId)
                          : '← Сначала введите ID сообщества'}
                      </code>
                      {vkEdit.vkGroupId && (
                        <button className={styles.copyBtn}
                          onClick={() => copy(getWebhookUrl(vkEdit.vkGroupId!), 'url' + c.id)}>
                          {copied === 'url' + c.id ? '✓' : 'Копировать'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Step 4: Confirmation code */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>4</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Скопируйте «Строку подтверждения» из VK и вставьте сюда</p>
                    <input className={styles.vkInput} placeholder="Строка подтверждения из VK"
                      value={vkEdit.vkConfirmCode ?? ''}
                      onChange={e => setVkEdit(p => ({ ...p, vkConfirmCode: e.target.value }))} />
                  </div>
                </div>

                {/* Step 5: Secret key (optional) */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>5</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Секретный ключ (необязательно, но рекомендуется)</p>
                    <p className={styles.stepDesc}>
                      Придумайте любую строку, вставьте в VK и сюда — для защиты вебхука
                    </p>
                    <input className={styles.vkInput} placeholder="Любая строка, например: mySecret123"
                      value={vkEdit.vkSecretKey ?? ''}
                      onChange={e => setVkEdit(p => ({ ...p, vkSecretKey: e.target.value }))} />
                  </div>
                </div>

                {/* Step 6: Access token */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>6</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Ключ доступа сообщества</p>
                    <p className={styles.stepDesc}>
                      VK → Управление → Работа с API → <b>Ключи доступа</b> → Создать ключ.<br />
                      Разрешите: <b>Сообщения сообщества</b>
                    </p>
                    <input className={styles.vkInput} type="password"
                      placeholder="vk1.a.xxxxx..."
                      value={vkEdit.vkAccessToken ?? ''}
                      onChange={e => setVkEdit(p => ({ ...p, vkAccessToken: e.target.value }))} />
                  </div>
                </div>

                {/* Step 7: Enable messages */}
                <div className={styles.step}>
                  <div className={styles.stepNum}>7</div>
                  <div className={styles.stepBody}>
                    <p className={styles.stepTitle}>Включите события в VK</p>
                    <p className={styles.stepDesc}>
                      В VK Callback API нажмите <b>«Подтвердить»</b>, затем во вкладке <b>«Типы событий»</b>{' '}
                      включите <b>«Входящее сообщение»</b>
                    </p>
                  </div>
                </div>

                <button className={styles.saveVKBtn} onClick={() => saveVK(c)}>
                  Сохранить и подключить VK ✓
                </button>

                {/* Prompt editor */}
                <div className={styles.promptSection}>
                  <p className={styles.stepTitle}>Системный промт заведения</p>
                  <textarea rows={5} className={styles.vkInput} defaultValue={c.systemPrompt}
                    onBlur={e => fetch(`/api/client/${c.apiKey}`, {
                      method: 'PATCH', headers: hdrs(),
                      body: JSON.stringify({ systemPrompt: e.target.value }),
                    })} />
                  <p className={styles.stepDesc}>Изменения сохраняются автоматически при выходе из поля</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
