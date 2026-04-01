import { NextRequest } from 'next/server';
import OpenAI from 'openai';

function getClient() {
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY ?? '' });
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
  const { message, systemPrompt } = body as { message: string; systemPrompt?: string };

  if (!message || typeof message !== 'string') {
    return new Response(JSON.stringify({ error: 'Invalid message' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const finalPrompt = systemPrompt?.trim() || DEFAULT_PROMPT;

  if (!process.env.OPENAI_API_KEY) {
    const fallback = 'Добрый день! Я помогу ответить на ваши вопросы о нашем заведении. Спросите о меню, ценах или условиях доставки.';
    return new Response(
      `data: ${JSON.stringify({ choices: [{ delta: { content: fallback } }] })}\n\ndata: [DONE]\n\n`,
      { headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' } }
    );
  }

  const stream = await getClient().chat.completions.create({
    model: 'gpt-4o',
    stream: true,
    temperature: 0.65,
    max_tokens: 250,
    messages: [
      { role: 'system', content: finalPrompt },
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
