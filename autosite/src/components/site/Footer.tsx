"use client";

import { Camera, Mail, MapPin, Phone, Play, Send } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

const columns = [
  {
    title: "Каталог",
    links: [
      { label: "Кроссоверы",   href: "/catalog" },
      { label: "Седаны",       href: "/catalog" },
      { label: "Внедорожники", href: "/catalog" },
      { label: "Премиум",      href: "/catalog" },
    ],
  },
  {
    title: "Услуги",
    links: [
      { label: "Подбор авто", href: "/services" },
      { label: "Трейд‑ин",   href: "/services" },
      { label: "Кредит",     href: "/services" },
      { label: "Диагностика",href: "/services" },
    ],
  },
  {
    title: "Компания",
    links: [
      { label: "О нас",     href: "/about" },
      { label: "Гарантии",  href: "/about" },
      { label: "Партнёры",  href: "/about" },
      { label: "Вакансии",  href: "/about" },
    ],
  },
] as const;

const socials = [
  { Icon: Send,   label: "Telegram" },
  { Icon: Camera, label: "Instagram" },
  { Icon: Play,   label: "YouTube" },
] as const;

export function Footer() {
  return (
    <footer className="relative overflow-hidden bg-[#000e1f]">
      {/* Top accent line */}
      <div className="relative h-[3px] w-full overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-accent to-transparent" />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 py-14 sm:py-16">
        <div className="grid gap-10 lg:grid-cols-12">
          {/* Brand */}
          <div className="lg:col-span-4">
            <Link href="/" className="inline-flex items-center gap-3 group">
              <div className="flex h-9 w-9 items-center justify-center bg-accent text-white relative overflow-hidden">
                <motion.div
                  className="absolute inset-0 bg-white/20"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: "100%" }}
                  transition={{ duration: 0.4 }}
                />
                <span className="relative font-black text-sm">A</span>
              </div>
              <div>
                <div className="text-[13px] font-black uppercase tracking-[0.2em] text-white">AUTOSITE</div>
                <div className="text-[10px] text-white/30 tracking-[0.15em] uppercase">Premium Auto</div>
              </div>
            </Link>

            <p className="mt-5 max-w-xs text-[13px] leading-6 text-white/40">
              Надёжные автомобили с честной диагностикой и прозрачными условиями. Выбирайте уверенно.
            </p>

            {/* Socials */}
            <div className="mt-6 flex gap-2">
              {socials.map(({ Icon, label }) => (
                <a
                  key={label}
                  href="#"
                  aria-label={label}
                  className="group flex h-9 w-9 items-center justify-center border border-white/[0.08] bg-white/[0.03] text-white/40 transition-all hover:border-accent/40 hover:bg-accent/10 hover:text-accent"
                >
                  <Icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:col-span-5">
            {columns.map((col) => (
              <div key={col.title}>
                <div className="text-[10px] font-bold uppercase tracking-[0.28em] text-white/25 mb-4">
                  {col.title}
                </div>
                <ul className="space-y-2.5">
                  {col.links.map((l) => (
                    <li key={l.label}>
                      <Link
                        href={l.href}
                        className="group flex items-center gap-2 text-[13px] text-white/45 transition-colors hover:text-white"
                      >
                        <span className="h-[1px] w-3 bg-white/15 transition-all group-hover:w-5 group-hover:bg-accent" />
                        {l.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Contacts */}
          <div className="lg:col-span-3">
            <div className="text-[10px] font-bold uppercase tracking-[0.28em] text-white/25 mb-4">Контакты</div>
            <div className="space-y-4">
              <div className="flex items-start gap-3 text-[13px] text-white/45">
                <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-accent/60" />
                <span>Москва, ул. Примерная, 10</span>
              </div>
              <a href="tel:+79990000000" className="flex items-center gap-3 text-[13px] text-white/45 transition-colors hover:text-white">
                <Phone className="h-4 w-4 shrink-0 text-accent/60" />
                <span>+7 (999) 000‑00‑00</span>
              </a>
              <a href="mailto:sales@autosite.ru" className="flex items-center gap-3 text-[13px] text-white/45 transition-colors hover:text-white">
                <Mail className="h-4 w-4 shrink-0 text-accent/60" />
                <span>sales@autosite.ru</span>
              </a>
            </div>

            {/* CTA card */}
            <div className="mt-6 border border-accent/20 bg-accent/5 p-4">
              <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-accent/80 mb-2">Остались вопросы?</div>
              <Link href="/contacts"
                className="inline-flex items-center gap-2 text-[13px] font-black uppercase tracking-[0.1em] text-white hover:text-accent transition-colors">
                Заказать звонок →
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col gap-3 border-t border-white/[0.05] pt-6 text-[12px] text-white/20 sm:flex-row sm:items-center sm:justify-between">
          <span>© {new Date().getFullYear()} AUTOSITE. Все права защищены.</span>
          <div className="flex gap-5">
            <Link href="/about" className="hover:text-white/50 transition-colors">Политика конфиденциальности</Link>
            <Link href="/contacts" className="hover:text-white/50 transition-colors">Контакты</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
