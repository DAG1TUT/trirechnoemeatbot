'use client';

import { useState, useRef, useCallback } from 'react';
import ChatBubble, { Message } from './ChatBubble';
import styles from '@/styles/glasschat.module.scss';

const SUGGESTED = [
  'Как работают авто-ответы?',
  'Как захватить лидов?',
  'Как настроить под доставку?',
];

interface GlassChatProps {
  onBotFlash?: () => void;
  systemPrompt?: string;
}

export default function GlassChat({ onBotFlash, systemPrompt }: GlassChatProps) {
  const [messages, setMessages] = useState<Message[]>([{
    id: 'intro', role: 'bot',
    text: 'Привет! Я Блик — AI-ассистент для автоматизации продаж в VK. Спросите о возможностях.',
    streaming: false,
  }]);
  const [input, setInput]    = useState('');
  const [thinking, setThink] = useState(false);

  const msgsRef  = useRef<HTMLDivElement>(null); // messages container
  const abortRef = useRef<AbortController | null>(null);

  // Scroll only inside the messages div — no page jump
  const scrollEnd = useCallback(() => {
    if (!msgsRef.current) return;
    msgsRef.current.scrollTop = msgsRef.current.scrollHeight;
  }, []);

  const send = useCallback(async (text: string) => {
    if (!text.trim() || thinking) return;

    setMessages(p => [...p, { id: Date.now().toString(), role: 'user', text: text.trim(), streaming: false }]);
    setInput('');
    setThink(true);
    setTimeout(scrollEnd, 30);

    const botId = (Date.now() + 1).toString();
    // Start bot message with streaming flag — ChatBubble shows plain text during stream
    setMessages(p => [...p, { id: botId, role: 'bot', text: '', streaming: true }]);

    try {
      abortRef.current = new AbortController();
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim(), systemPrompt }),
        signal: abortRef.current.signal,
      });

      if (!res.ok || !res.body) throw new Error('api error');

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let acc = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const raw = decoder.decode(value, { stream: true });
        for (const line of raw.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const d = line.slice(6).trim();
          if (d === '[DONE]') break;
          try {
            const token = JSON.parse(d).choices?.[0]?.delta?.content;
            if (token) {
              acc += token;
              setMessages(p => p.map(m => m.id === botId ? { ...m, text: acc } : m));
              scrollEnd();
            }
          } catch { /* ignore parse errors */ }
        }
      }

      // Mark done — keep streaming:false so ChatBubble shows text as-is (no re-animation)
      setMessages(p => p.map(m => m.id === botId ? { ...m, streaming: false } : m));
      onBotFlash?.();

    } catch (e: unknown) {
      if (e instanceof Error && e.name === 'AbortError') return;
      setMessages(p => p.map(m => m.id === botId
        ? { ...m, text: 'Ошибка соединения. Попробуйте ещё раз.', streaming: false } : m));
    } finally {
      setThink(false);
      setTimeout(scrollEnd, 50);
    }
  }, [thinking, systemPrompt, onBotFlash, scrollEnd]);

  return (
    <div className={styles.panel}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.dot} data-thinking={thinking} />
        <span className={styles.title}>Live Demo Chat</span>
        <button className={styles.menu} aria-label="Меню">
          <span/><span/><span/>
        </button>
      </div>

      {/* Messages — ref on the container, not on a child sentinel */}
      <div ref={msgsRef} className={styles.messages}>
        {messages.map(m => <ChatBubble key={m.id} message={m} />)}
        {thinking && !messages.some(m => m.streaming) && (
          <div className={styles.thinking}><span/><span/><span/></div>
        )}
      </div>

      {/* Chips — only before first user message */}
      {messages.filter(m => m.role === 'user').length < 1 && (
        <div className={styles.chips}>
          {SUGGESTED.map(s => (
            <button key={s} className={styles.chip} onClick={() => send(s)}>{s}</button>
          ))}
        </div>
      )}

      {/* Input */}
      <form className={styles.form} onSubmit={e => { e.preventDefault(); send(input); }}>
        <textarea
          className={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input); } }}
          placeholder="Напишите сообщение…"
          rows={1}
          disabled={thinking}
        />
        <button type="submit" className={styles.send} disabled={!input.trim() || thinking} aria-label="Отправить">
          <svg viewBox="0 0 20 20" fill="none" width={16} height={16}>
            <path d="M17 10L3 3l2.5 7L3 17l14-7z" stroke="currentColor" strokeWidth={1.6} strokeLinejoin="round"/>
          </svg>
        </button>
      </form>
    </div>
  );
}
