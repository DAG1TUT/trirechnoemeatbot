"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, Fuel, Gauge, LayoutGrid, List, Settings2, SlidersHorizontal, X, Zap } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";
import { type BodyType, type Fuel as FuelType, type InventoryItem, type Transmission } from "@/content/inventory";

function formatRub(v: number) {
  return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(v);
}
function formatKm(v: number) {
  return new Intl.NumberFormat("ru-RU").format(v);
}

type ViewMode = "grid" | "list";

const BODIES: BodyType[] = ["Кроссовер", "Седан", "Внедорожник", "Хэтчбек", "Универсал", "Купе"];
const FUELS: FuelType[] = ["Бензин", "Дизель", "Гибрид", "Электро"];
const TRANSMISSIONS: Transmission[] = ["Автомат", "Механика", "Робот"];

const PRICE_MIN = 0;
const PRICE_MAX = 20_000_000;

type Filters = {
  brands: string[];
  bodies: BodyType[];
  fuels: FuelType[];
  transmissions: Transmission[];
  priceMin: number;
  priceMax: number;
  search: string;
};

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "h-8 whitespace-nowrap px-3 text-[11px] font-bold uppercase tracking-[0.12em] border transition-all",
        active
          ? "border-accent bg-accent text-white"
          : "border-black/10 bg-white text-slate-600 hover:border-accent/50 hover:text-navy",
      ].join(" ")}
    >
      {children}
    </button>
  );
}

function toggle<T>(arr: T[], val: T): T[] {
  return arr.includes(val) ? arr.filter((v) => v !== val) : [...arr, val];
}

export function CatalogClient({ cars }: { cars: InventoryItem[] }) {
  const BRANDS = useMemo(() => [...new Set(cars.map((c) => c.brand))].sort(), [cars]);

  const [view, setView] = useState<ViewMode>("grid");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filters, setFilters] = useState<Filters>({
    brands: [],
    bodies: [],
    fuels: [],
    transmissions: [],
    priceMin: PRICE_MIN,
    priceMax: PRICE_MAX,
    search: "",
  });

  const activeCount =
    filters.brands.length +
    filters.bodies.length +
    filters.fuels.length +
    filters.transmissions.length +
    (filters.priceMin > PRICE_MIN || filters.priceMax < PRICE_MAX ? 1 : 0) +
    (filters.search ? 1 : 0);

  function reset() {
    setFilters({ brands: [], bodies: [], fuels: [], transmissions: [], priceMin: PRICE_MIN, priceMax: PRICE_MAX, search: "" });
  }

  const items = useMemo(() => {
    return cars.filter((c) => {
      if (filters.brands.length && !filters.brands.includes(c.brand)) return false;
      if (filters.bodies.length && !filters.bodies.includes(c.body)) return false;
      if (filters.fuels.length && !filters.fuels.includes(c.fuel)) return false;
      if (filters.transmissions.length && !filters.transmissions.includes(c.transmission)) return false;
      if (c.priceRub < filters.priceMin || c.priceRub > filters.priceMax) return false;
      if (filters.search) {
        const q = filters.search.toLowerCase();
        if (!c.name.toLowerCase().includes(q) && !c.brand.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [filters, cars]);

  return (
    <section className="bg-[#f6f7f9] py-10 sm:py-14">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">

        {/* Toolbar */}
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="search"
              value={filters.search}
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
              placeholder="Поиск по марке или модели…"
              className="h-10 w-full border border-black/[0.09] bg-white pl-4 pr-10 text-sm text-navy placeholder-slate-400 outline-none transition focus:border-accent"
            />
            {filters.search && (
              <button
                type="button"
                onClick={() => setFilters((f) => ({ ...f, search: "" }))}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-navy"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          <motion.button
            whileTap={{ scale: 0.95 }}
            type="button"
            onClick={() => setFiltersOpen((v) => !v)}
            className={[
              "flex h-10 items-center gap-2 border px-4 text-[12px] font-bold uppercase tracking-[0.12em] transition-all",
              filtersOpen || activeCount > 0
                ? "border-accent bg-accent text-white"
                : "border-black/10 bg-white text-slate-600 hover:border-accent/50",
            ].join(" ")}
          >
            <SlidersHorizontal className="h-4 w-4" />
            Фильтры
            {activeCount > 0 && (
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white text-[10px] font-black text-accent">
                {activeCount}
              </span>
            )}
          </motion.button>

          <div className="flex border border-black/[0.09] bg-white">
            {(["grid", "list"] as ViewMode[]).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setView(m)}
                className={[
                  "flex h-10 w-10 items-center justify-center transition-colors",
                  view === m ? "bg-navy text-white" : "text-slate-400 hover:text-navy",
                ].join(" ")}
                aria-label={m === "grid" ? "Сетка" : "Список"}
              >
                {m === "grid" ? <LayoutGrid className="h-4 w-4" /> : <List className="h-4 w-4" />}
              </button>
            ))}
          </div>

          <div className="ml-auto text-[13px] font-semibold text-slate-500">
            {items.length} {items.length === 1 ? "автомобиль" : items.length < 5 ? "автомобиля" : "автомобилей"}
          </div>
        </div>

        {/* Filter panel */}
        <AnimatePresence>
          {filtersOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <div className="mb-6 border border-black/[0.07] bg-white p-5">
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <div className="mb-3 text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Марка</div>
                    <div className="flex flex-wrap gap-1.5">
                      {BRANDS.map((b) => (
                        <Chip
                          key={b}
                          active={filters.brands.includes(b)}
                          onClick={() => setFilters((f) => ({ ...f, brands: toggle(f.brands, b) }))}
                        >
                          {b}
                        </Chip>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="mb-3 text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Кузов</div>
                    <div className="flex flex-wrap gap-1.5">
                      {BODIES.map((b) => (
                        <Chip
                          key={b}
                          active={filters.bodies.includes(b)}
                          onClick={() => setFilters((f) => ({ ...f, bodies: toggle(f.bodies, b) }))}
                        >
                          {b}
                        </Chip>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="mb-3 text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Топливо</div>
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {FUELS.map((f) => (
                        <Chip
                          key={f}
                          active={filters.fuels.includes(f)}
                          onClick={() => setFilters((prev) => ({ ...prev, fuels: toggle(prev.fuels, f) }))}
                        >
                          {f}
                        </Chip>
                      ))}
                    </div>
                    <div className="text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400 mb-3">КПП</div>
                    <div className="flex flex-wrap gap-1.5">
                      {TRANSMISSIONS.map((t) => (
                        <Chip
                          key={t}
                          active={filters.transmissions.includes(t)}
                          onClick={() => setFilters((f) => ({ ...f, transmissions: toggle(f.transmissions, t) }))}
                        >
                          {t}
                        </Chip>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="mb-3 text-[10px] font-bold uppercase tracking-[0.24em] text-slate-400">Цена</div>
                    <div className="space-y-3">
                      {(["priceMin", "priceMax"] as const).map((key) => (
                        <div key={key}>
                          <div className="mb-1 flex justify-between text-[11px] text-slate-500">
                            <span>{key === "priceMin" ? "От" : "До"}</span>
                            <span className="font-bold text-navy">{formatRub(filters[key])}</span>
                          </div>
                          <input
                            type="range"
                            min={PRICE_MIN}
                            max={PRICE_MAX}
                            step={100000}
                            value={filters[key]}
                            onChange={(e) =>
                              setFilters((f) => ({ ...f, [key]: Number(e.target.value) }))
                            }
                            className="w-full accent-accent h-1"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {activeCount > 0 && (
                  <div className="mt-5 flex justify-end border-t border-black/[0.06] pt-4">
                    <button
                      type="button"
                      onClick={reset}
                      className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.12em] text-slate-400 hover:text-accent transition-colors"
                    >
                      <X className="h-3.5 w-3.5" />
                      Сбросить фильтры
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* No results */}
        {items.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center gap-4 py-24 text-center"
          >
            <div className="text-5xl">🔍</div>
            <div className="text-lg font-black uppercase text-navy">Ничего не найдено</div>
            <div className="text-sm text-slate-500">Попробуйте изменить фильтры</div>
            <button
              type="button"
              onClick={reset}
              className="mt-2 flex h-10 items-center gap-2 bg-accent px-6 text-[12px] font-black uppercase tracking-[0.12em] text-white"
            >
              Сбросить
            </button>
          </motion.div>
        )}

        {/* Grid */}
        {view === "grid" && items.length > 0 && (
          <motion.div layout className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            <AnimatePresence mode="popLayout">
              {items.map((car, i) => (
                <motion.article
                  key={car.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.3, delay: i * 0.04, ease: [0.22, 1, 0.36, 1] }}
                  whileHover={{ y: -5 }}
                  className="group overflow-hidden bg-white border border-black/[0.06] shadow-[0_4px_18px_rgba(0,0,0,0.05)] hover:shadow-[0_18px_48px_rgba(0,0,0,0.12)] transition-shadow"
                >
                  <div className="relative h-48 overflow-hidden bg-[#f0f1f3]">
                    <Image
                      src={car.imageSrc}
                      alt={car.name}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-[1.06]"
                    />
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-t from-navy/80 via-navy/20 to-transparent"
                      initial={{ opacity: 0 }}
                      whileHover={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    />
                    <div className="absolute left-0 top-3 flex flex-col gap-1">
                      <span className="bg-navy px-3 py-1 text-[10px] font-black uppercase tracking-[0.14em] text-white">
                        {car.year}
                      </span>
                      {car.new && (
                        <span className="bg-accent px-3 py-1 text-[10px] font-black uppercase tracking-[0.14em] text-white">
                          Новинка
                        </span>
                      )}
                    </div>
                    <motion.div
                      initial={{ y: 10, opacity: 0 }}
                      whileHover={{ y: 0, opacity: 1 }}
                      transition={{ duration: 0.25 }}
                      className="absolute bottom-3 left-3 right-3 flex items-end justify-between"
                    >
                      <span className="text-xl font-black text-white">{formatRub(car.priceRub)}</span>
                      <Link
                        href="/contacts"
                        className="flex h-8 w-8 items-center justify-center bg-accent text-white hover:bg-white hover:text-accent transition-colors"
                      >
                        <ArrowUpRight className="h-4 w-4" />
                      </Link>
                    </motion.div>
                  </div>

                  <div className="p-4">
                    <h3 className="text-[14px] font-black uppercase tracking-tight text-navy leading-snug">
                      {car.name}
                    </h3>
                    <div className="mt-2 text-[11px] font-semibold text-slate-400 uppercase tracking-[0.14em]">
                      {car.body} · {car.color}
                    </div>
                    <div className="mt-3 grid grid-cols-3 gap-1.5">
                      {[
                        { Icon: Gauge,     val: `${formatKm(car.mileageKm)} км` },
                        { Icon: Settings2, val: car.transmission },
                        { Icon: Fuel,      val: car.fuel },
                      ].map(({ Icon, val }) => (
                        <div key={val} className="flex flex-col items-center gap-1 bg-[#f6f7f9] py-2">
                          <Icon className="h-3.5 w-3.5 text-accent" />
                          <span className="text-[9px] font-semibold text-slate-500 text-center leading-tight">{val}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 flex items-center justify-between border-t border-black/[0.06] pt-3">
                      <div className="flex items-center gap-1 text-[11px] text-slate-400">
                        <Zap className="h-3.5 w-3.5 text-accent" />
                        {car.powerHp} л.с.
                      </div>
                      <div className="text-base font-black text-accent">{formatRub(car.priceRub)}</div>
                    </div>
                  </div>
                </motion.article>
              ))}
            </AnimatePresence>
          </motion.div>
        )}

        {/* List view */}
        {view === "list" && items.length > 0 && (
          <div className="flex flex-col gap-3">
            <AnimatePresence mode="popLayout">
              {items.map((car, i) => (
                <motion.article
                  key={car.id}
                  layout
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 16 }}
                  transition={{ duration: 0.28, delay: i * 0.03 }}
                  className="group flex gap-0 overflow-hidden bg-white border border-black/[0.06] hover:border-accent/30 hover:shadow-[0_8px_32px_rgba(0,0,0,0.08)] transition-all"
                >
                  <div className="relative h-auto w-40 shrink-0 overflow-hidden bg-[#f0f1f3] sm:w-52">
                    <Image
                      src={car.imageSrc}
                      alt={car.name}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-[1.05]"
                    />
                    {car.new && (
                      <span className="absolute left-0 top-2 bg-accent px-2 py-0.5 text-[9px] font-black uppercase tracking-wider text-white">
                        Новинка
                      </span>
                    )}
                  </div>

                  <div className="flex flex-1 flex-col justify-between p-4 sm:p-5">
                    <div>
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">{car.brand} · {car.year}</div>
                          <h3 className="mt-0.5 text-[15px] font-black uppercase tracking-tight text-navy">{car.name}</h3>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">Цена</div>
                          <div className="text-lg font-black text-accent">{formatRub(car.priceRub)}</div>
                        </div>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {[
                          `${formatKm(car.mileageKm)} км`,
                          car.transmission,
                          car.fuel,
                          car.body,
                          `${car.powerHp} л.с.`,
                        ].map((tag) => (
                          <span key={tag} className="bg-[#f6f7f9] px-2.5 py-1 text-[10px] font-semibold text-slate-500">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="mt-3 flex items-center justify-between border-t border-black/[0.06] pt-3">
                      <span className="text-[11px] font-semibold text-slate-400">{car.color}</span>
                      <Link
                        href="/contacts"
                        className="group/btn flex items-center gap-1.5 text-[12px] font-black uppercase tracking-[0.1em] text-navy/60 hover:text-accent transition-colors"
                      >
                        Узнать цену
                        <ArrowUpRight className="h-3.5 w-3.5 transition-transform group-hover/btn:-translate-y-0.5 group-hover/btn:translate-x-0.5" />
                      </Link>
                    </div>
                  </div>
                </motion.article>
              ))}
            </AnimatePresence>
          </div>
        )}

      </div>
    </section>
  );
}
