import { NextRequest } from 'next/server';

const TG_API = 'https://api.telegram.org';

function escape(text: string) {
  return text.replace(/[_*[\]()~`>#+\-=|{}.!\\]/g, '\\$&');
}

export async function POST(req: NextRequest) {
  const { name, phone, email, businessType, businessName } = await req.json() as {
    name: string;
    phone?: string;
    email?: string;
    businessType?: string;
    businessName?: string;
  };

  if (!name?.trim()) {
    return Response.json({ error: 'name required' }, { status: 400 });
  }

  const token  = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!token || !chatId) {
    // Env vars not set — silently succeed so the UI flow isn't broken
    console.warn('[lead] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set');
    return Response.json({ ok: true });
  }

  const now = new Date().toLocaleString('ru-RU', {
    timeZone: 'Europe/Moscow',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });

  const lines = [
    `🔔 *Новая заявка — Блик*`,
    ``,
    `👤 *Имя:* ${escape(name.trim())}`,
    phone?.trim() ? `📞 *Телефон:* ${escape(phone.trim())}` : null,
    email?.trim() ? `📧 *Email:* ${escape(email.trim())}` : null,
    businessName?.trim() ? `🏪 *Заведение:* ${escape(businessName.trim())}` : null,
    businessType?.trim() ? `🍱 *Тип бизнеса:* ${escape(businessType.trim())}` : null,
    ``,
    `🕐 ${escape(now)} \\(МСК\\)`,
  ].filter(l => l !== null).join('\n');

  const res = await fetch(`${TG_API}/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: lines,
      parse_mode: 'MarkdownV2',
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    console.error('[lead] Telegram API error:', err);
    return Response.json({ error: 'telegram error' }, { status: 502 });
  }

  return Response.json({ ok: true });
}
