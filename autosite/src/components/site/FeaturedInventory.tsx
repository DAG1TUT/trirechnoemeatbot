"use client";

import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { ArrowUpRight, Fuel, Gauge, Settings2, Star } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRef } from "react";
import { type InventoryItem, featuredInventory } from "@/content/inventory";
import { Reveal } from "@/components/motion/Reveal";

function formatRub(value: number) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("ru-RU").format(value);
}

function TiltCard({ car, index }: { car: InventoryItem; index: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useSpring(useTransform(y, [-80, 80], [5, -5]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(x, [-80, 80], [-5, 5]), { stiffness: 300, damping: 30 });

  function onMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    x.set(e.clientX - rect.left - rect.width / 2);
    y.set(e.clientY - rect.top - rect.height / 2);
  }
  function onMouseLeave() {
    x.set(0);
    y.set(0);
  }

  return (
    <Reveal
      transition={{ delay: index * 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    >
      <motion.div
        ref={ref}
        style={{ rotateX, rotateY, transformPerspective: 900, transformStyle: "preserve-3d" }}
        onMouseMove={onMouseMove}
        onMouseLeave={onMouseLeave}
        whileHover={{ y: -6 }}
        transition={{ duration: 0.2 }}
        className="group relative overflow-hidden bg-white border border-black/[0.06] shadow-[0_8px_32px_rgba(0,0,0,0.07)] hover:shadow-[0_24px_56px_rgba(0,0,0,0.14)] transition-shadow"
      >
        {/* Image */}
        <div className="relative h-52 overflow-hidden bg-muted sm:h-60">
          <Image
            src={car.imageSrc}
            alt={car.name}
            fill
            className="object-cover transition-transform duration-700 ease-out group-hover:scale-[1.07]"
          />
          {/* Overlay on hover */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-t from-navy/80 via-navy/30 to-transparent"
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            transition={{ duration: 0.35 }}
          />

          {/* Year badge */}
          <div className="absolute left-0 top-4 bg-navy px-4 py-1.5 text-[11px] font-black uppercase tracking-[0.18em] text-white">
            {car.year}
          </div>

          {/* Price on image hover */}
          <motion.div
            initial={{ y: 12, opacity: 0 }}
            whileHover={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="absolute bottom-4 left-0 right-0 flex items-end justify-between px-4"
          >
            <div className="text-2xl font-black text-white">{formatRub(car.priceRub)}</div>
            <Link href="/catalog" className="flex h-9 w-9 items-center justify-center bg-accent text-white hover:bg-accent-light transition-colors">
              <ArrowUpRight className="h-4 w-4" />
            </Link>
          </motion.div>
        </div>

        {/* Body */}
        <div className="p-5">
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-[15px] font-black uppercase tracking-tight text-navy leading-snug">{car.name}</h3>
            <div className="flex items-center gap-1 text-accent shrink-0">
              <Star className="h-3.5 w-3.5 fill-current" />
              <span className="text-xs font-bold">4.9</span>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-3 gap-2">
            {[
              { Icon: Gauge, value: `${formatNumber(car.mileageKm)} км` },
              { Icon: Settings2, value: car.transmission },
              { Icon: Fuel, value: car.fuel },
            ].map(({ Icon, value }) => (
              <div key={value} className="flex flex-col items-center gap-1 bg-muted px-2 py-2.5">
                <Icon className="h-3.5 w-3.5 text-accent" />
                <span className="text-[10px] font-semibold text-slate-600 text-center leading-tight">{value}</span>
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between border-t border-black/[0.06] pt-4">
            <div>
              <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">Цена</div>
              <div className="text-lg font-black text-accent">{formatRub(car.priceRub)}</div>
            </div>
            <Link
              href="/catalog"
              className="group/btn flex items-center gap-2 border border-navy/15 px-4 py-2 text-[12px] font-bold uppercase tracking-[0.1em] text-navy/70 transition-all hover:border-accent hover:bg-accent hover:text-white"
            >
              Подробнее
              <ArrowUpRight className="h-3.5 w-3.5 transition-transform group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5" />
            </Link>
          </div>
        </div>
      </motion.div>
    </Reveal>
  );
}

export function FeaturedInventory({ cars = featuredInventory }: { cars?: InventoryItem[] }) {
  return (
    <section className="bg-[#f6f7f9] py-16 sm:py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        {/* Header */}
        <Reveal>
          <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between mb-10">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="h-[2px] w-8 bg-accent" />
                <span className="text-[11px] font-bold uppercase tracking-[0.25em] text-accent">В наличии</span>
              </div>
              <h2 className="text-2xl font-black uppercase tracking-tight text-navy sm:text-3xl lg:text-4xl">
                Избранные автомобили
              </h2>
              <p className="mt-2 max-w-md text-sm text-slate-500">
                Подборка с честной диагностикой и прозрачными условиями покупки.
              </p>
            </div>
            <Link
              href="/catalog"
              className="group flex shrink-0 items-center gap-2 border-b-2 border-accent pb-0.5 text-[13px] font-black uppercase tracking-[0.12em] text-navy transition-colors hover:text-accent"
            >
              Весь каталог
              <ArrowUpRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </Link>
          </div>
        </Reveal>

        {/* Grid */}
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {cars.map((car, i) => (
            <TiltCard key={car.id} car={car} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
