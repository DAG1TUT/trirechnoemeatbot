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
  // Completed messages — never mutated during streaming
  const [messages, setMessages] = useState<Message[]>([{
    id: 'intro', role: 'bot',
    text: 'Привет! Я Блик — AI-ассистент для автоматизации продаж в VK. Спросите о возможностях.',
    streaming: false,
  }]);

  // Streaming bot reply — separate state so only this bubble re-renders
  const [stream, setStream] = useState<{ text: string; active: boolean }>({ text: '', active: false });

  const [input, setInput]    = useState('');
  const [thinking, setThink] = useState(false);

  const msgsRef  = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  // Accumulate tokens in a ref — flush to state via rAF to avoid per-token renders
  const accRef   = useRef('');
  const rafRef   = useRef<number | null>(null);

  const scrollEnd = useCallback(() => {
    if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight;
  }, []);

  const flushAcc = useCallback(() => {
    setStream({ text: accRef.current, active: true });
    scrollEnd();
    rafRef.current = null;
  }, [scrollEnd]);

  const send = useCallback(async (text: string) => {
    if (!text.trim() || thinking) return;

    const userMsg: Message = {
      id: `u_${Date.now()}`,
      role: 'user',
      text: text.trim(),
      streaming: false,
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setThink(true);
    setStream({ text: '', active: true });
    accRef.current = '';
    setTimeout(scrollEnd, 30);

    try {
      abortRef.current?.abort();
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
              accRef.current += token;
              // Throttle: schedule one rAF per batch of tokens
              if (!rafRef.current) {
                rafRef.current = requestAnimationFrame(flushAcc);
              }
            }
          } catch { /* ignore parse errors */ }
        }
      }

      // Cancel any pending rAF and do a final flush
      if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }

      const finalText = accRef.current;

      // Move completed message into the messages array; clear streaming state
      setMessages(prev => [...prev, {
        id: `b_${Date.now()}`,
        role: 'bot',
        text: finalText,
        streaming: false,
      }]);
      setStream({ text: '', active: false });
      onBotFlash?.();

    } catch (e: unknown) {
      if (e instanceof Error && e.name === 'AbortError') return;
      setMessages(prev => [...prev, {
        id: `b_err_${Date.now()}`,
        role: 'bot',
        text: 'Ошибка соединения. Попробуйте ещё раз.',
        streaming: false,
      }]);
      setStream({ text: '', active: false });
    } finally {
      setThink(false);
      setTimeout(scrollEnd, 50);
    }
  }, [thinking, systemPrompt, onBotFlash, scrollEnd, flushAcc]);

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

      {/* Messages */}
      <div ref={msgsRef} className={styles.messages}>
        {/* Completed messages — never re-render during streaming */}
        {messages.map(m => <ChatBubble key={m.id} message={m} />)}

        {/* Live streaming bubble — only this re-renders during streaming */}
        {stream.active && (
          stream.text
            ? <ChatBubble
                key="streaming"
                message={{ id: 'streaming', role: 'bot', text: stream.text, streaming: true }}
              />
            : <div className={styles.thinking}><span/><span/><span/></div>
        )}
      </div>

      {/* Chips */}
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
        <button type="submit" className={styles.send}
          disabled={!input.trim() || thinking} aria-label="Отправить">
          <svg viewBox="0 0 20 20" fill="none" width={16} height={16}>
            <path d="M17 10L3 3l2.5 7L3 17l14-7z" stroke="currentColor" strokeWidth={1.6} strokeLinejoin="round"/>
          </svg>
        </button>
      </form>
    </div>
  );
}
