"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import { Reveal } from "@/components/motion/Reveal";
import { type Testimonial, testimonials as staticTestimonials } from "@/content/testimonials";

export function TestimonialsSlider({ testimonials = staticTestimonials }: { testimonials?: Testimonial[] }) {
  const [index, setIndex] = useState(0);
  const [dir, setDir] = useState(1);
  const active = testimonials[index]!;

  useEffect(() => {
    const t = window.setInterval(() => {
      setDir(1);
      setIndex((v) => (v + 1) % testimonials.length);
    }, 9000);
    return () => window.clearInterval(t);
  }, [testimonials.length]);

  function prev() {
    setDir(-1);
    setIndex((v) => (v - 1 + testimonials.length) % testimonials.length);
  }
  function next() {
    setDir(1);
    setIndex((v) => (v + 1) % testimonials.length);
  }

  const variants = {
    enter: (d: number) => ({ opacity: 0, x: d * 40, filter: "blur(4px)" }),
    center: { opacity: 1, x: 0, filter: "blur(0px)" },
    exit: (d: number) => ({ opacity: 0, x: d * -40, filter: "blur(4px)" }),
  };

  return (
    <section className="relative overflow-hidden bg-[#001124] py-16 sm:py-20 noise">
      {/* Grid pattern */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />
      <div className="absolute -right-20 top-1/2 h-96 w-96 -translate-y-1/2 rounded-full bg-accent/8 blur-[120px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6">
        {/* Header row */}
        <Reveal className="flex items-end justify-between mb-12">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <span className="h-[2px] w-8 bg-accent" />
              <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-accent">Отзывы</span>
            </div>
            <h2 className="text-2xl font-black uppercase tracking-tight text-white sm:text-3xl lg:text-4xl">
              Счастливые<br /> покупатели
            </h2>
          </div>
          <div className="hidden sm:flex items-center gap-2">
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={prev}
              className="flex h-11 w-11 items-center justify-center border border-white/10 bg-white/[0.04] text-white/50 transition-all hover:border-accent/50 hover:text-accent"
              aria-label="Предыдущий"
            >
              <ChevronLeft className="h-4 w-4" />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={next}
              className="flex h-11 w-11 items-center justify-center border border-white/10 bg-white/[0.04] text-white/50 transition-all hover:border-accent/50 hover:text-accent"
              aria-label="Следующий"
            >
              <ChevronRight className="h-4 w-4" />
            </motion.button>
          </div>
        </Reveal>

        <div className="grid gap-6 lg:grid-cols-12">
          {/* Main quote */}
          <div className="lg:col-span-8">
            <div className="relative overflow-hidden border border-white/[0.06] bg-white/[0.03] backdrop-blur-sm p-8 sm:p-10 min-h-[220px]">
              {/* Large quote mark */}
              <div className="absolute left-6 top-4 text-[80px] font-black leading-none text-accent/10 select-none">&ldquo;</div>

              <AnimatePresence mode="wait" custom={dir}>
                <motion.div
                  key={active.id}
                  custom={dir}
                  variants={variants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                >
                  <p className="relative text-lg font-semibold leading-8 text-white/85 sm:text-xl sm:leading-9">
                    &ldquo;{active.text}&rdquo;
                  </p>

                  <div className="mt-8 flex items-center gap-4">
                    {/* Avatar placeholder */}
                    <div className="flex h-10 w-10 items-center justify-center bg-accent/20 text-sm font-black text-accent border border-accent/20">
                      {active.name.charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-black uppercase tracking-[0.1em] text-white">{active.name}</div>
                      <div className="text-[12px] text-white/40">{active.city} · {active.car}</div>
                    </div>

                    {/* Stars */}
                    <div className="ml-auto flex gap-1">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <div key={i} className="h-1.5 w-1.5 rounded-full bg-accent" />
                      ))}
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* Sidebar list */}
          <div className="lg:col-span-4 flex flex-col gap-3">
            {testimonials.map((t, i) => (
              <motion.button
                key={t.id}
                whileHover={{ x: 3 }}
                onClick={() => { setDir(i > index ? 1 : -1); setIndex(i); }}
                className={[
                  "group text-left border p-4 transition-all",
                  i === index
                    ? "border-accent/40 bg-accent/10"
                    : "border-white/[0.06] bg-white/[0.02] hover:border-white/15",
                ].join(" ")}
                aria-label={`Отзыв ${t.name}`}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <div className={`h-1.5 w-1.5 rounded-full ${i === index ? "bg-accent" : "bg-white/20"}`} />
                  <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/40">{t.name}</span>
                </div>
                <div className="line-clamp-2 text-[13px] text-white/60 leading-5">{t.text}</div>
              </motion.button>
            ))}

            {/* Mobile arrows */}
            <div className="flex items-center gap-2 sm:hidden">
              <motion.button whileTap={{ scale: 0.9 }} onClick={prev}
                className="flex h-11 w-11 items-center justify-center border border-white/10 text-white/50 hover:text-accent transition-colors"
                aria-label="Предыдущий">
                <ChevronLeft className="h-4 w-4" />
              </motion.button>
              <motion.button whileTap={{ scale: 0.9 }} onClick={next}
                className="flex h-11 w-11 items-center justify-center border border-white/10 text-white/50 hover:text-accent transition-colors"
                aria-label="Следующий">
                <ChevronRight className="h-4 w-4" />
              </motion.button>
            </div>
          </div>
        </div>

        {/* Progress dots */}
        <div className="mt-8 flex items-center gap-2">
          {testimonials.map((_, i) => (
            <button
              key={i}
              onClick={() => { setDir(i > index ? 1 : -1); setIndex(i); }}
              className={`h-[3px] transition-all ${i === index ? "w-8 bg-accent" : "w-4 bg-white/15"}`}
              aria-label={`Перейти к отзыву ${i + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
