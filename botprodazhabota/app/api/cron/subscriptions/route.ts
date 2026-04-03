import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';

const TG_API = 'https://api.telegram.org';

function esc(t: string) {
  return t.replace(/[_*[\]()~`>#+\-=|{}.!\\]/g, '\\$&');
}

async function sendTg(text: string) {
  const token  = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) return;

  await fetch(`${TG_API}/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'MarkdownV2' }),
  });
}

function daysBetween(a: Date, b: Date) {
  return Math.ceil((b.getTime() - a.getTime()) / 86400000);
}

export async function GET(req: NextRequest) {
  const secret = req.headers.get('x-cron-secret') || req.nextUrl.searchParams.get('secret');
  if (process.env.CRON_SECRET && secret !== process.env.CRON_SECRET) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const in3days = new Date(now);
  in3days.setDate(in3days.getDate() + 3);

  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const endOfToday = new Date(startOfToday);
  endOfToday.setDate(endOfToday.getDate() + 1);

  const clients = await prisma.client.findMany({
    where: {
      isActive: true,
      subscriptionEndsAt: { not: null, lte: in3days },
    },
    select: {
      businessName: true,
      subscriptionEndsAt: true,
      vkGroupId: true,
    },
  });

  if (clients.length === 0) {
    return Response.json({ ok: true, notified: 0 });
  }

  const expired: string[] = [];
  const today: string[] = [];
  const soon: string[] = [];

  for (const c of clients) {
    const end = c.subscriptionEndsAt!;
    const days = daysBetween(startOfToday, end);
    const name = esc(c.businessName);
    const vk = c.vkGroupId ? ` \\(VK: ${esc(c.vkGroupId)}\\)` : '';

    if (days < 0) {
      expired.push(`  • ${name}${vk} — истекла ${esc(Math.abs(days).toString())} дн\\. назад`);
    } else if (days === 0) {
      today.push(`  • ${name}${vk} — *сегодня\\!*`);
    } else {
      soon.push(`  • ${name}${vk} — через ${esc(days.toString())} дн\\.`);
    }
  }

  const sections: string[] = ['⏰ *Отчёт по подпискам — Блик*', ''];

  if (expired.length) {
    sections.push('🔴 *Истекли:*', ...expired, '');
  }
  if (today.length) {
    sections.push('🟡 *Истекают сегодня:*', ...today, '');
  }
  if (soon.length) {
    sections.push('🟢 *Истекают в ближайшие 3 дня:*', ...soon, '');
  }

  await sendTg(sections.join('\n'));

  return Response.json({ ok: true, notified: clients.length });
}
