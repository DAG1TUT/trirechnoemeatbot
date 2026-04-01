"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { Reveal } from "@/components/motion/Reveal";
import { whyUs } from "@/content/whyus";

export function WhyUs() {
  return (
    <section className="bg-white py-16 sm:py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="grid gap-14 lg:grid-cols-12 lg:gap-16">

          {/* Left sticky column */}
          <div className="lg:col-span-5">
            <Reveal>
              <div className="flex items-center gap-3 mb-4">
                <span className="h-[2px] w-8 bg-accent" />
                <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-accent">Преимущества</span>
              </div>
              <h2 className="text-2xl font-black uppercase tracking-tight text-navy sm:text-3xl lg:text-4xl">
                Почему<br className="hidden lg:block" /> выбирают<br className="hidden lg:block" /> нас
              </h2>
              <p className="mt-4 max-w-sm text-sm leading-6 text-slate-500">
                Сервис выстроен вокруг доверия: прозрачная диагностика, понятные условия и скорость сделки.
              </p>

              {/* Квадраты-акценты */}
              <div className="mt-10 flex gap-3">
                {[
                  { num: "100%", label: "Проверка" },
                  { num: "0", label: "Скрытых\nкомиссий" },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="flex-1 border border-navy/10 bg-navy/[0.03] p-4"
                  >
                    <div className="text-2xl font-black text-accent">{item.num}</div>
                    <div className="mt-1 text-[11px] font-bold uppercase tracking-[0.12em] text-navy/50 whitespace-pre-line leading-tight">{item.label}</div>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <Link
                  href="/about"
                  className="group inline-flex items-center gap-2 text-[13px] font-black uppercase tracking-[0.12em] text-navy/60 hover:text-navy transition-colors"
                >
                  О компании
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </div>
            </Reveal>
          </div>

          {/* Right grid */}
          <div className="lg:col-span-7">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
              {whyUs.map((item, idx) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.2 }}
                  transition={{ delay: idx * 0.07, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
                  whileHover={{ y: -3 }}
                  className="group relative overflow-hidden border border-black/[0.07] bg-[#f9f9fb] p-5 transition-shadow hover:shadow-[0_12px_32px_rgba(0,0,0,0.08)]"
                >
                  {/* Accent top-left bar */}
                  <div className="absolute left-0 top-0 h-full w-[3px] bg-gradient-to-b from-accent to-accent/0 opacity-0 transition-opacity group-hover:opacity-100" />

                  <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center bg-navy text-white group-hover:bg-accent transition-colors duration-300">
                      <item.Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-[13px] font-black uppercase tracking-[0.08em] text-navy leading-snug">
                        {item.title}
                      </h3>
                      <p className="mt-2 text-[13px] leading-5 text-slate-500">
                        {item.text}
                      </p>
                    </div>
                  </div>

                  {/* Index number bg */}
                  <div className="absolute right-3 bottom-3 text-[48px] font-black leading-none text-black/[0.03] select-none">
                    {String(idx + 1).padStart(2, "0")}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
