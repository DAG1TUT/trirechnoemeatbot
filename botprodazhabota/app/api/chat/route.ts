import { NextRequest } from 'next/server';
import OpenAI from 'openai';
import { prisma } from '@/lib/prisma';

function getClient() {
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY ?? '' });
}

function moscowTime() {
  return new Intl.DateTimeFormat('ru-RU', {
    timeZone: 'Europe/Moscow',
    weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date());
}

const DEFAULT_PROMPT = `Ты — умный AI-ассистент для VK-сообщества заведения общепита.

Твоя задача — отвечать на сообщения клиентов в VK: рассказывать о меню, составе блюд, ценах, времени работы, условиях доставки и других вопросах о заведении.

Правила:
- Отвечай дружелюбно и вежливо
- Будь конкретным и полезным
- Если не знаешь — честно скажи, что уточнишь у менеджера
- Не придумывай цены и детали, которых нет в описании заведения
- Отвечай ТОЛЬКО по-русски
- Длина ответа: 1–3 предложения, по делу`;

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { message, systemPrompt: inlinePrompt, apiKey } = body as {
    message: string;
    systemPrompt?: string;
    apiKey?: string;
  };

  if (!message || typeof message !== 'string') {
    return new Response(JSON.stringify({ error: 'Invalid message' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // 1. If apiKey provided — fetch system prompt from DB
  let finalPrompt = inlinePrompt?.trim() || DEFAULT_PROMPT;

  if (apiKey) {
    try {
      const client = await prisma.client.findUnique({
        where: { apiKey, isActive: true },
        select: { systemPrompt: true },
      });
      if (client?.systemPrompt) {
        finalPrompt = client.systemPrompt;
      }
    } catch (e) {
      console.error('[chat] DB lookup failed:', e);
      // fall through to default
    }
  }

  if (!process.env.OPENAI_API_KEY) {
    const fallback = 'Добрый день! Я помогу ответить на ваши вопросы о нашем заведении. Спросите о меню, ценах или условиях доставки.';
    return new Response(
      `data: ${JSON.stringify({ choices: [{ delta: { content: fallback } }] })}\n\ndata: [DONE]\n\n`,
      { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' } }
    );
  }

  const timeContext = `\n\nСейчас: ${moscowTime()} (Москва). Учитывай текущее время при ответах — например, если заведение закрыто, сообщи об этом.`;

  const stream = await getClient().chat.completions.create({
    model: 'gpt-4o',
    stream: true,
    temperature: 0.65,
    max_tokens: 250,
    messages: [
      { role: 'system', content: finalPrompt + timeContext },
      { role: 'user',   content: message },
    ],
  });

  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      try {
        for await (const chunk of stream) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(chunk)}\n\n`));
        }
        controller.enqueue(encoder.encode('data: [DONE]\n\n'));
      } finally {
        controller.close();
      }
    },
  });

  return new Response(readable, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' },
  });
}
