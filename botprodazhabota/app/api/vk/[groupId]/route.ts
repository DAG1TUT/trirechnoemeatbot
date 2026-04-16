import { NextRequest, after } from 'next/server';
import { prisma } from '@/lib/prisma';
import OpenAI from 'openai';

const VK_API = 'https://api.vk.com/method';
const VK_VERSION = '5.199';

const OPENAI_TIMEOUT_MS = 30_000;
const VK_FETCH_TIMEOUT_MS = 15_000;
const VK_RETRY_ATTEMPTS = 2;

function openai() {
  return new OpenAI({
    apiKey: process.env.OPENAI_API_KEY ?? '',
    timeout: OPENAI_TIMEOUT_MS,
    maxRetries: 2,
  });
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

  for (let attempt = 1; attempt <= VK_RETRY_ATTEMPTS; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), VK_FETCH_TIMEOUT_MS);
    try {
      const res = await fetch(`${VK_API}/messages.send?${params}`, {
        signal: controller.signal,
      });
      const json = await res.json();
      if (json.error) {
        console.error('[vk] messages.send error:', json.error);
      }
      return;
    } catch (e) {
      console.error(`[vk] sendVK attempt ${attempt}/${VK_RETRY_ATTEMPTS} failed:`, e);
      if (attempt === VK_RETRY_ATTEMPTS) throw e;
      await new Promise(r => setTimeout(r, 1_000 * attempt));
    } finally {
      clearTimeout(timer);
    }
  }
}

/* ── Get AI reply ─────────────────────────────────────────────────── */
function moscowTime() {
  const now = new Date();
  const fmt = new Intl.DateTimeFormat('ru-RU', {
    timeZone: 'Europe/Moscow',
    weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
  return fmt.format(now);
}

async function getAIReply(userMessage: string, systemPrompt: string): Promise<string> {
  if (!process.env.OPENAI_API_KEY) {
    return 'Добрый день! Чем могу помочь?';
  }
  const timeContext = `\n\nСейчас: ${moscowTime()} (Москва). Учитывай текущее время при ответах — например, если заведение закрыто, сообщи об этом.`;
  try {
    const res = await openai().chat.completions.create({
      model: 'gpt-4o',
      temperature: 0.65,
      max_tokens: 300,
      messages: [
        { role: 'system', content: systemPrompt + timeContext },
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

  // VK всегда присылает group_id в теле. URL может быть скопирован с другой группы —
  // ищем клиента по group_id из JSON, иначе по сегменту пути.
  const gidFromBody =
    body.group_id != null ? String(body.group_id).trim() : null;
  const gidFromPath = String(groupId).trim();
  const lookupId = gidFromBody || gidFromPath;

  if (gidFromBody && gidFromPath && gidFromBody !== gidFromPath) {
    console.warn(
      '[vk] URL groupId mismatch body.group_id — using body:',
      gidFromPath,
      '→',
      gidFromBody
    );
  }

  const client = await prisma.client.findFirst({
    where: { vkGroupId: lookupId, isActive: true },
  });

  if (!client) {
    console.warn('[vk] Unknown group — lookupId:', lookupId, 'path:', gidFromPath);
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

    // Use after() so the background work survives after the response is sent
    after(async () => {
      try {
        const reply = await getAIReply(text, client.systemPrompt);
        if (client.vkAccessToken) {
          await sendVK(client.vkAccessToken, fromId, reply);
        } else {
          console.error('[vk] No vkAccessToken for client', client.businessName, client.id);
        }
      } catch (e) {
        console.error('[vk] background handler error:', e);
      }
    });
  }

  return new Response('ok');
}
