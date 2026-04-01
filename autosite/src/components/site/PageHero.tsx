"use client";

import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight } from "lucide-react";
import Link from "next/link";

export function PageHero({
  kicker,
  title,
  description,
}: {
  kicker: string;
  title: string;
  description: string;
}) {
  return (
    <section className="relative overflow-hidden bg-[#001124] pt-[70px] noise">
      <div className="pointer-events-none absolute inset-0 opacity-[0.05]"
        style={{ background: "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(255,107,0,0.3), transparent)" }}
      />
      <div className="absolute -left-20 bottom-0 h-64 w-64 rounded-full bg-accent/8 blur-[80px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 py-16 sm:py-20">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="flex items-center gap-3 mb-5">
            <span className="h-[2px] w-8 bg-accent" />
            <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-accent">{kicker}</span>
          </div>

          <h1 className="text-3xl font-black uppercase tracking-tight text-white sm:text-4xl lg:text-5xl">
            {title}
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-white/50 sm:text-base sm:leading-7">
            {description}
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/" className="group flex h-11 items-center gap-2 border border-white/10 bg-white/[0.04] px-5 text-[13px] font-bold uppercase tracking-[0.1em] text-white/60 transition-all hover:border-white/25 hover:text-white">
              <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
              На главную
            </Link>
            <Link href="/contacts" className="relative group flex h-11 items-center gap-2 overflow-hidden bg-accent px-5 text-[13px] font-black uppercase tracking-[0.1em] text-white">
              <motion.span className="absolute inset-0 bg-white/15" initial={{ x: "-100%" }} whileHover={{ x: "100%" }} transition={{ duration: 0.4 }} />
              <span className="relative">Заказать звонок</span>
              <ArrowRight className="relative h-4 w-4" />
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Diagonal bottom cut */}
      <div className="h-12 bg-[#f6f7f9]" style={{ clipPath: "polygon(0 100%, 100% 0, 100% 100%)" }} />
    </section>
  );
}
