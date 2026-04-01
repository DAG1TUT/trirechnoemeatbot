import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import OpenAI from 'openai';

const VK_API = 'https://api.vk.com/method';
const VK_VERSION = '5.199';

function openai() {
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY ?? '' });
}

/* ── Send a message back to VK user ──────────────────────────────── */
async function sendVK(token: string, userId: number, text: string) {
  const params = new URLSearchParams({
    user_id:   String(userId),
    message:   text,
    random_id: String(Math.floor(Math.random() * 1e9)),
    access_token: token,
    v: VK_VERSION,
  });
  const res = await fetch(`${VK_API}/messages.send?${params}`);
  const json = await res.json();
  if (json.error) console.error('[vk] messages.send error:', json.error);
}

/* ── Get AI reply ─────────────────────────────────────────────────── */
async function getAIReply(userMessage: string, systemPrompt: string): Promise<string> {
  if (!process.env.OPENAI_API_KEY) {
    return 'Добрый день! Чем могу помочь?';
  }
  try {
    const res = await openai().chat.completions.create({
      model: 'gpt-4o',
      temperature: 0.65,
      max_tokens: 300,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user',   content: userMessage },
      ],
    });
    return res.choices[0]?.message?.content?.trim() ?? 'Спасибо за обращение!';
  } catch (e) {
    console.error('[vk] OpenAI error:', e);
    return 'Извините, произошла ошибка. Попробуйте ещё раз.';
  }
}

/* ── VK Callback handler ──────────────────────────────────────────── */
export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ groupId: string }> }
) {
  const { groupId } = await params;
  let body: Record<string, unknown>;

  try {
    body = await req.json();
  } catch {
    return new Response('bad request', { status: 400 });
  }

  // Find client by VK group ID
  const client = await prisma.client.findFirst({
    where: { vkGroupId: groupId, isActive: true },
  });

  if (!client) {
    console.warn('[vk] Unknown group:', groupId);
    return new Response('ok'); // Don't expose 404 to VK
  }

  // Verify secret key (optional but recommended)
  if (client.vkSecretKey && body.secret !== client.vkSecretKey) {
    return new Response('forbidden', { status: 403 });
  }

  // ── Confirmation handshake ──────────────────────────────────────
  if (body.type === 'confirmation') {
    return new Response(client.vkConfirmCode ?? 'ok', {
      headers: { 'Content-Type': 'text/plain' },
    });
  }

  // Always respond "ok" to VK immediately (5s timeout)
  // Process message in background
  if (body.type === 'message_new') {
    const msgObj = (body.object as Record<string, unknown>);
    const message = (msgObj.message ?? msgObj) as Record<string, unknown>;
    const text     = String(message.text ?? '').trim();
    const fromId   = Number(message.from_id);

    // Skip: empty, outgoing, or bot messages
    if (!text || !fromId || fromId < 0 || message.out === 1) {
      return new Response('ok');
    }

    // Fire and forget — don't await (VK needs "ok" within 5s)
    (async () => {
      try {
        const reply = await getAIReply(text, client.systemPrompt);
        if (client.vkAccessToken) {
          await sendVK(client.vkAccessToken, fromId, reply);
        }
      } catch (e) {
        console.error('[vk] background handler error:', e);
      }
    })();
  }

  return new Response('ok');
}
