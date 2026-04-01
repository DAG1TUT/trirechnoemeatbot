'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import styles from '@/styles/chatbubble.module.scss';

export interface Message {
  id: string;
  role: 'user' | 'bot';
  text: string;
  streaming?: boolean;
}

export default function ChatBubble({ message }: { message: Message }) {
  const rowRef    = useRef<HTMLDivElement>(null);
  const didEnter  = useRef(false);   // run entrance only once

  useEffect(() => {
    if (didEnter.current || !rowRef.current) return;
    didEnter.current = true;
    gsap.fromTo(rowRef.current,
      { scale: .72, opacity: 0, filter: 'blur(5px)',
        transformOrigin: message.role === 'user' ? 'right bottom' : 'left bottom' },
      { scale: 1, opacity: 1, filter: 'blur(0px)', duration: .46, ease: 'back.out(1.6)' }
    );
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div ref={rowRef}
      className={`${styles.row} ${message.role === 'user' ? styles.u : styles.b}`}>
      {message.role === 'bot' && <div className={styles.avatar}>AI</div>}
      <div className={`${styles.bubble} ${message.role === 'user' ? styles.u : styles.b}`}>
        {/* Always render plain text — no SplitReveal re-play after stream ends */}
        <span>{message.text}</span>
      </div>
    </div>
  );
}
