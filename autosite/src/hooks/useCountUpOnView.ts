"use client";

import { useInView } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";

export function useCountUpOnView<T extends Element = HTMLElement>({
  to,
  durationMs = 1100,
  start = 0,
}: {
  to: number;
  durationMs?: number;
  start?: number;
}) {
  const ref = useRef<T | null>(null);
  const inView = useInView(ref, { amount: 0.35, once: true });
  const [value, setValue] = useState(start);

  const clampTo = useMemo(() => Math.max(0, Math.floor(to)), [to]);

  useEffect(() => {
    if (!inView) return;

    const from = start;
    const target = clampTo;
    const startAt = performance.now();
    let raf = 0;

    const tick = (now: number) => {
      const t = Math.min(1, (now - startAt) / durationMs);
      const eased = 1 - Math.pow(1 - t, 3);
      const next = Math.round(from + (target - from) * eased);
      setValue(next);
      if (t < 1) raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [clampTo, durationMs, inView, start]);

  return { ref, value, inView };
}

