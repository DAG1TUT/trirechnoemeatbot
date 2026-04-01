"use client";

import { AnimatePresence, motion, useScroll, useTransform } from "framer-motion";
import { Menu, Phone, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const nav = [
  { href: "/catalog", label: "Каталог" },
  { href: "/services", label: "Услуги" },
  { href: "/about", label: "О компании" },
  { href: "/contacts", label: "Контакты" },
] as const;

export function Header() {
  const [, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { scrollY } = useScroll();
  const headerOpacity = useTransform(scrollY, [0, 80], [0, 1]);

  useEffect(() => {
    const unsub = scrollY.on("change", (v) => setScrolled(v > 20));
    return unsub;
  }, [scrollY]);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50">
        {/* blur/fill backdrop — фейдится поверх */}
        <motion.div
          style={{ opacity: headerOpacity }}
          className="absolute inset-0 bg-[#001124]/90 backdrop-blur-xl border-b border-white/[0.06]"
        />

        <div className="relative mx-auto flex h-[70px] max-w-7xl items-center justify-between px-4 sm:px-6">
          {/* Logo */}
          <Link href="/" aria-label="На главную" className="group flex items-center gap-3">
            <div className="relative flex h-9 w-9 items-center justify-center overflow-hidden bg-accent">
              <motion.div
                className="absolute inset-0 bg-white/20"
                initial={{ x: "-100%" }}
                whileHover={{ x: "100%" }}
                transition={{ duration: 0.4, ease: "easeInOut" }}
              />
              <span className="relative font-black text-white text-sm tracking-wider">A</span>
            </div>
            <div>
              <div className="text-[13px] font-black uppercase tracking-[0.2em] text-white leading-none">AUTOSITE</div>
              <div className="text-[10px] font-medium text-white/40 tracking-[0.15em] uppercase leading-none mt-0.5">Premium Auto</div>
            </div>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden lg:flex items-center gap-8">
            {nav.map((item) => (
              <Link key={item.href} href={item.href} className="group relative py-2">
                <span className="text-[13px] font-bold uppercase tracking-[0.12em] text-white/70 transition-colors group-hover:text-white">
                  {item.label}
                </span>
                <span className="absolute bottom-0 left-0 h-[2px] w-0 bg-accent transition-all duration-300 group-hover:w-full" />
              </Link>
            ))}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <a
              href="tel:+79990000000"
              className="hidden sm:flex items-center gap-2 text-white/60 hover:text-white transition-colors"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-accent/15 ring-1 ring-accent/30">
                <Phone className="h-3.5 w-3.5 text-accent" />
              </div>
              <span className="text-[13px] font-semibold">+7 (999) 000‑00‑00</span>
            </a>

            <Link
              href="/contacts"
              className="hidden lg:flex relative group h-9 items-center overflow-hidden bg-accent px-5"
            >
              <motion.span
                className="absolute inset-0 bg-white/15"
                initial={{ x: "-100%" }}
                whileHover={{ x: "100%" }}
                transition={{ duration: 0.4 }}
              />
              <span className="relative text-[12px] font-black uppercase tracking-[0.14em] text-white">
                Заказать звонок
              </span>
            </Link>

            {/* Burger */}
            <motion.button
              type="button"
              whileTap={{ scale: 0.92 }}
              onClick={() => setOpen(true)}
              className="flex h-10 w-10 items-center justify-center border border-white/10 bg-white/5 text-white/80 hover:bg-white/10 hover:text-white transition-colors lg:hidden"
              aria-label="Открыть меню"
            >
              <Menu className="h-5 w-5" />
            </motion.button>
          </div>
        </div>
      </header>

      {/* Mobile drawer */}
      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed inset-0 z-[60] lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="absolute inset-0 bg-black/70 backdrop-blur-sm"
              onClick={() => setOpen(false)}
            />
            <motion.aside
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 280 }}
              className="absolute right-0 top-0 h-full w-80 bg-[#001124] border-l border-white/[0.07] flex flex-col"
            >
              <div className="flex items-center justify-between px-6 py-5 border-b border-white/[0.07]">
                <span className="text-xs font-bold uppercase tracking-[0.22em] text-white/40">Навигация</span>
                <motion.button
                  whileTap={{ scale: 0.9, rotate: 90 }}
                  onClick={() => setOpen(false)}
                  className="flex h-9 w-9 items-center justify-center border border-white/10 text-white/60 hover:text-white transition-colors"
                  aria-label="Закрыть"
                >
                  <X className="h-4 w-4" />
                </motion.button>
              </div>

              <div className="flex-1 px-6 py-8 space-y-1">
                {nav.map((item, i) => (
                  <motion.div
                    key={item.href}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                  >
                    <Link
                      href={item.href}
                      onClick={() => setOpen(false)}
                      className="group flex items-center justify-between border-b border-white/[0.06] py-4 text-sm font-bold uppercase tracking-[0.12em] text-white/60 hover:text-white transition-colors"
                    >
                      {item.label}
                      <span className="text-accent text-lg leading-none transition-transform group-hover:translate-x-1">→</span>
                    </Link>
                  </motion.div>
                ))}
              </div>

              <div className="px-6 pb-8 space-y-4">
                <Link
                  href="/contacts"
                  onClick={() => setOpen(false)}
                  className="flex w-full items-center justify-center bg-accent py-3 text-[13px] font-black uppercase tracking-[0.14em] text-white"
                >
                  Заказать звонок
                </Link>
                <div className="rounded-lg bg-white/[0.04] p-4 border border-white/[0.06]">
                  <div className="text-[10px] uppercase tracking-[0.22em] text-white/30 font-semibold">Телефон</div>
                  <a href="tel:+79990000000" className="mt-1 block text-base font-black text-white">
                    +7 (999) 000‑00‑00
                  </a>
                </div>
              </div>
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
