"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

const slides = [
  { id: "s1", imageSrc: "/cars/hero-1.svg", tag: "Премиальный подбор", tagNum: "01" },
  { id: "s2", imageSrc: "/cars/hero-2.svg", tag: "Проверенная история", tagNum: "02" },
  { id: "s3", imageSrc: "/cars/hero-3.svg", tag: "Быстрая сделка",     tagNum: "03" },
] as const;

const DURATION = 6000;

export function HeroSlider() {
  const [index, setIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const rafRef = useRef<number>(0);
  const startRef = useRef<number>(0);

  const goTo = useCallback((i: number) => {
    setIndex(i);
    setProgress(0);
    startRef.current = performance.now();
  }, []);

  useEffect(() => {
    const tick = (now: number) => {
      const elapsed = now - startRef.current;
      const p = Math.min(elapsed / DURATION, 1);
      setProgress(p);
      if (p >= 1) {
        setIndex((v) => (v + 1) % slides.length);
        setProgress(0);
        startRef.current = performance.now();
      }
      rafRef.current = requestAnimationFrame(tick);
    };
    startRef.current = performance.now();
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  const active = slides[index]!;

  return (
    <section className="relative h-screen min-h-[640px] overflow-hidden bg-[#00111f]">
      {/* Background */}
      <AnimatePresence mode="sync">
        <motion.div
          key={active.id + "-bg"}
          className="absolute inset-0"
          initial={{ opacity: 0, scale: 1.06 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
        >
          <Image src={active.imageSrc} alt="" fill className="object-cover" priority />
          <div className="absolute inset-0 bg-gradient-to-r from-[#00111f] via-[#00111f]/75 to-[#00111f]/20" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#00111f]/80 via-transparent to-[#00111f]/30" />
          {/* Orange flare */}
          <div className="absolute -left-32 top-1/4 h-[500px] w-[500px] rounded-full bg-accent/10 blur-[120px]" />
        </motion.div>
      </AnimatePresence>

      {/* Diagonal decorative slice */}
      <div className="pointer-events-none absolute inset-y-0 right-0 w-1/3 bg-gradient-to-l from-[#00111f]/60 to-transparent" />
      <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#00111f] to-transparent" />

      {/* Content */}
      <div className="relative z-10 flex h-full flex-col justify-end pb-16 sm:pb-20 lg:pb-24">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 items-end gap-10">

            {/* Left: main text */}
            <div>
              {/* Tag */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={active.id + "-tag"}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                  className="mb-5 flex items-center gap-3"
                >
                  <span className="text-[11px] font-black uppercase tracking-[0.3em] text-accent">{active.tagNum}</span>
                  <span className="h-px w-10 bg-accent/50" />
                  <span className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/50">{active.tag}</span>
                </motion.div>
              </AnimatePresence>

              {/* Headline */}
              <AnimatePresence mode="wait">
                <motion.h1
                  key={active.id + "-h1"}
                  initial={{ opacity: 0, y: 30, clipPath: "inset(100% 0% 0% 0%)" }}
                  animate={{ opacity: 1, y: 0, clipPath: "inset(0% 0% 0% 0%)" }}
                  exit={{ opacity: 0, y: -20, clipPath: "inset(0% 0% 100% 0%)" }}
                  transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
                  className="text-4xl font-black uppercase leading-[1.05] tracking-tight text-white sm:text-5xl lg:text-6xl xl:text-7xl"
                >
                  ВАШ НОВЫЙ<br />
                  <span className="text-accent">АВТОМОБИЛЬ</span><br />
                  НАЧИНАЕТСЯ<br />ЗДЕСЬ
                </motion.h1>
              </AnimatePresence>

              {/* Sub */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.8 }}
                className="mt-5 max-w-md text-sm leading-6 text-white/55 sm:text-base sm:leading-7"
              >
                Надёжные автомобили с честной диагностикой, быстрым&nbsp;оформлением и поддержкой 24/7.
              </motion.p>

              {/* CTA */}
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.45, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="mt-8 flex flex-wrap gap-3"
              >
                <Link
                  href="/catalog"
                  className="group relative flex h-12 items-center gap-3 overflow-hidden bg-accent px-6 text-[13px] font-black uppercase tracking-[0.14em] text-white"
                >
                  <motion.span
                    className="absolute inset-0 bg-white/15"
                    initial={{ x: "-100%" }}
                    whileHover={{ x: "100%" }}
                    transition={{ duration: 0.45 }}
                  />
                  <span className="relative">Смотреть каталог</span>
                  <motion.span
                    className="relative"
                    initial={{ x: 0 }}
                    whileHover={{ x: 3 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ArrowRight className="h-4 w-4" />
                  </motion.span>
                </Link>
                <Link
                  href="/contacts"
                  className="flex h-12 items-center gap-2 border border-white/20 px-6 text-[13px] font-bold uppercase tracking-[0.14em] text-white/70 transition-all hover:border-accent/50 hover:text-white"
                >
                  Получить предложение
                </Link>
              </motion.div>
            </div>

            {/* Right: info card + slider controls */}
            <div className="hidden lg:block">
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                className="ml-auto max-w-xs border border-white/[0.08] bg-white/[0.04] backdrop-blur-md p-6"
              >
                <div className="text-[10px] font-bold uppercase tracking-[0.28em] text-white/30 mb-4">Быстрый старт</div>
                <div className="space-y-4">
                  {[
                    ["Подбор авто", "15 минут"],
                    ["Диагностика", "В день обращения"],
                    ["Оформление", "Без очередей"],
                  ].map(([label, val]) => (
                    <div key={label} className="flex items-center justify-between gap-4 border-b border-white/[0.06] pb-4 last:border-0 last:pb-0">
                      <span className="text-sm text-white/50">{label}</span>
                      <span className="text-sm font-bold text-white">{val}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>

          {/* Slider controls */}
          <div className="mt-10 flex items-center gap-5">
            {/* Prev/Next */}
            <button
              type="button"
              onClick={() => goTo((index - 1 + slides.length) % slides.length)}
              className="flex h-10 w-10 items-center justify-center border border-white/10 bg-white/[0.04] text-white/60 transition hover:border-accent/50 hover:text-accent"
              aria-label="Предыдущий"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => goTo((index + 1) % slides.length)}
              className="flex h-10 w-10 items-center justify-center border border-white/10 bg-white/[0.04] text-white/60 transition hover:border-accent/50 hover:text-accent"
              aria-label="Следующий"
            >
              <ChevronRight className="h-4 w-4" />
            </button>

            {/* Progress dots */}
            <div className="flex items-center gap-3">
              {slides.map((s, i) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => goTo(i)}
                  className="group relative h-[3px] overflow-hidden bg-white/15 transition-all"
                  style={{ width: i === index ? 56 : 24 }}
                  aria-label={`Слайд ${i + 1}`}
                >
                  {i === index && (
                    <motion.span
                      className="absolute inset-y-0 left-0 bg-accent"
                      style={{ width: `${progress * 100}%` }}
                    />
                  )}
                </button>
              ))}
            </div>

            <div className="ml-auto text-[12px] font-bold tracking-[0.22em] text-white/30">
              {String(index + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
