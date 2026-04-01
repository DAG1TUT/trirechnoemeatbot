"use client";

import { motion } from "framer-motion";
import { Mail, MapPin, Phone } from "lucide-react";
import { useState } from "react";
import { PageHero } from "@/components/site/PageHero";

const inputCls =
  "w-full border-0 border-b border-black/15 bg-transparent pb-2.5 pt-1 text-sm text-navy placeholder-slate-400 outline-none transition-colors focus:border-accent";
const labelCls = "block text-[11px] font-bold uppercase tracking-[0.22em] text-slate-400";

export default function ContactsPage() {
  const [sent, setSent] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSent(true);
  }

  return (
    <>
      <PageHero
        kicker="Контакты"
        title="СВЯЖИТЕСЬ С НАМИ"
        description="Оставьте заявку — перезвоним и предложим 3–5 лучших вариантов под бюджет и задачи."
      />

      <section className="bg-[#f6f7f9] py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid gap-6 lg:grid-cols-12">

            {/* Contact info */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
              className="lg:col-span-4"
            >
              <div className="h-full bg-[#001124] p-8 text-white">
                <div className="text-[10px] font-bold uppercase tracking-[0.28em] text-white/30 mb-6">
                  Контактная информация
                </div>

                <div className="space-y-6">
                  {[
                    { Icon: MapPin, label: "Адрес",   value: "Москва, ул. Примерная, 10", href: undefined },
                    { Icon: Phone, label: "Телефон",  value: "+7 (999) 000‑00‑00",        href: "tel:+79990000000" },
                    { Icon: Mail,  label: "Email",    value: "sales@autosite.ru",          href: "mailto:sales@autosite.ru" },
                  ].map(({ Icon, label, value, href }) => (
                    <div key={label} className="flex items-start gap-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center bg-accent/10 border border-accent/20">
                        <Icon className="h-4 w-4 text-accent" />
                      </div>
                      <div>
                        <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/30">{label}</div>
                        {href ? (
                          <a href={href} className="mt-0.5 block text-sm font-semibold text-white hover:text-accent transition-colors">{value}</a>
                        ) : (
                          <div className="mt-0.5 text-sm font-semibold text-white">{value}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-10 border-t border-white/[0.07] pt-6">
                  <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/30 mb-2">Режим работы</div>
                  <div className="text-sm text-white/60">Пн–Пт: 9:00 – 20:00</div>
                  <div className="text-sm text-white/60">Сб–Вс: 10:00 – 18:00</div>
                </div>
              </div>
            </motion.div>

            {/* Form */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
              className="lg:col-span-8"
            >
              <div className="bg-white border border-black/[0.06] p-8 sm:p-10">
                <div className="text-[10px] font-bold uppercase tracking-[0.28em] text-slate-400 mb-8">
                  Заявка на обратный звонок
                </div>

                {sent ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center py-12 gap-4 text-center"
                  >
                    <div className="flex h-16 w-16 items-center justify-center bg-accent text-white text-2xl font-black">✓</div>
                    <div className="text-lg font-black uppercase tracking-tight text-navy">Заявка отправлена!</div>
                    <div className="text-sm text-slate-500">Перезвоним вам в течение 15 минут.</div>
                  </motion.div>
                ) : (
                  <form onSubmit={handleSubmit} className="grid gap-8 sm:grid-cols-2">
                    <div>
                      <label className={labelCls}>Имя</label>
                      <input name="name" type="text" required placeholder="Как к вам обращаться?" autoComplete="name" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>Телефон</label>
                      <input name="phone" type="tel" required placeholder="+7 (___) ___‑__‑__" autoComplete="tel" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>Email</label>
                      <input name="email" type="email" placeholder="example@mail.ru" autoComplete="email" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>Удобное время</label>
                      <input name="time" type="text" placeholder="Напр.: 14:00 – 16:00" className={inputCls} />
                    </div>
                    <div className="sm:col-span-2">
                      <label className={labelCls}>Что ищете?</label>
                      <input
                        name="request"
                        type="text"
                        placeholder="Например: кроссовер до 5 млн, автомат, не старше 2021"
                        className={inputCls}
                      />
                    </div>

                    <div className="sm:col-span-2 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.97 }}
                        type="submit"
                        className="group relative flex h-12 items-center justify-center gap-3 overflow-hidden bg-accent px-8 text-[13px] font-black uppercase tracking-[0.14em] text-white"
                      >
                        <motion.span
                          className="absolute inset-0 bg-white/15"
                          initial={{ x: "-100%" }}
                          whileHover={{ x: "100%" }}
                          transition={{ duration: 0.45 }}
                        />
                        <span className="relative">Отправить заявку</span>
                      </motion.button>
                      <p className="text-[11px] text-slate-400">
                        Нажимая «Отправить», вы соглашаетесь на обработку персональных данных.
                      </p>
                    </div>
                  </form>
                )}
              </div>
            </motion.div>

          </div>
        </div>
      </section>
    </>
  );
}
