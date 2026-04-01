"use client";

import { motion } from "framer-motion";
import { Clock, Headset, Package, TrendingUp } from "lucide-react";
import { type RefObject } from "react";
import { useCountUpOnView } from "@/hooks/useCountUpOnView";

const stats = [
  {
    id: "st1",
    to: 1000,
    suffix: "+",
    label: "Авто в наличии",
    sub: "Готовы к выдаче сегодня",
    Icon: Package,
    color: "from-accent/20 to-accent/5",
  },
  {
    id: "st2",
    to: 15,
    suffix: "",
    label: "Лет на рынке",
    sub: "Опыт, которому доверяют",
    Icon: Clock,
    color: "from-blue-500/20 to-blue-500/5",
  },
  {
    id: "st3",
    value: "24/7",
    label: "Поддержка",
    sub: "Всегда на связи",
    Icon: Headset,
    color: "from-emerald-500/20 to-emerald-500/5",
  },
  {
    id: "st4",
    to: 98,
    suffix: "%",
    label: "Довольных клиентов",
    sub: "По итогам опросов 2024",
    Icon: TrendingUp,
    color: "from-purple-500/20 to-purple-500/5",
  },
] as const;

function CountStat({ to, suffix }: { to: number; suffix: string }) {
  const { ref, value } = useCountUpOnView<HTMLSpanElement>({ to, durationMs: 1400 });
  return (
    <span ref={ref as RefObject<HTMLSpanElement>}>
      {new Intl.NumberFormat("ru-RU").format(value)}{suffix}
    </span>
  );
}

export function StatsBlock() {
  return (
    <section className="relative overflow-hidden bg-[#001124] py-16 sm:py-20 noise">
      {/* Background pattern */}
      <div className="pointer-events-none absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage: "repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,0.5) 39px,rgba(255,255,255,0.5) 40px), repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,0.5) 39px,rgba(255,255,255,0.5) 40px)",
        }}
      />
      <div className="absolute -left-40 top-1/2 h-80 w-80 -translate-y-1/2 rounded-full bg-accent/10 blur-[100px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.25 }}
          transition={{ duration: 0.5 }}
          className="mb-10 flex items-center gap-3"
        >
          <span className="h-[2px] w-8 bg-accent" />
          <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-accent">Цифры</span>
        </motion.div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ delay: i * 0.1, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
              whileHover={{ y: -4, scale: 1.01 }}
              className={`relative overflow-hidden border border-white/[0.07] bg-gradient-to-br ${s.color} p-6 backdrop-blur-sm`}
            >
              {/* Corner accent */}
              <div className="absolute right-0 top-0 h-12 w-12 bg-white/[0.03]" style={{ clipPath: "polygon(100% 0, 0 0, 100% 100%)" }} />

              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 items-center justify-center bg-white/[0.06] border border-white/[0.08]">
                  <s.Icon className="h-5 w-5 text-white/60" />
                </div>
                <div className="h-1.5 w-1.5 rounded-full bg-accent/60" />
              </div>

              <div className="text-4xl font-black tracking-tight text-white sm:text-5xl">
                {"to" in s ? <CountStat to={s.to} suffix={s.suffix} /> : s.value}
              </div>

              <div className="mt-2 text-sm font-bold uppercase tracking-[0.1em] text-white/80">{s.label}</div>
              <div className="mt-1 text-[11px] text-white/35">{s.sub}</div>

              {/* Bottom accent line */}
              <motion.div
                className="absolute bottom-0 left-0 h-[2px] bg-accent/50"
                initial={{ width: 0 }}
                whileInView={{ width: "40%" }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 + 0.3, duration: 0.8 }}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
