/**
 * WordPress Headless API client.
 *
 * When WORDPRESS_URL is set this module fetches live data from the WP REST API
 * (/wp-json/autosite/v1/*) with ISR caching.  When it is not set — or when a
 * request fails — it transparently falls back to the bundled static data so
 * the site always works even without a WP instance.
 */

import type { InventoryItem } from "@/content/inventory";
import type { Testimonial } from "@/content/testimonials";
import { allInventory, featuredInventory } from "@/content/inventory";
import { testimonials as staticTestimonials } from "@/content/testimonials";

const WP_URL = process.env.WORDPRESS_URL?.replace(/\/$/, "") ?? "";
const REVALIDATE = Number(process.env.REVALIDATE_SECONDS ?? 60);

// ─── Generic fetch helper ──────────────────────────────────────────────────────

async function wpFetch<T>(path: string): Promise<T | null> {
  if (!WP_URL) return null;

  try {
    const res = await fetch(`${WP_URL}/wp-json/autosite/v1/${path}`, {
      next: { revalidate: REVALIDATE },
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

// ─── WordPress response shapes ────────────────────────────────────────────────

type WPCar = {
  id: string;
  name: string;
  brand: string;
  year: number;
  mileageKm: number;
  priceRub: number;
  powerHp: number;
  transmission: string;
  fuel: string;
  body: string;
  color: string;
  imageSrc: string;
  featured: boolean;
  new: boolean;
};

type WPReview = {
  id: string;
  name: string;
  city: string;
  car: string;
  text: string;
};

export type SiteSettings = {
  phone: string;
  email: string;
  address: string;
  hours: string;
};

// ─── Mappers ──────────────────────────────────────────────────────────────────

function mapCar(w: WPCar): InventoryItem {
  return {
    id: w.id,
    name: w.name,
    brand: w.brand,
    year: w.year,
    mileageKm: w.mileageKm,
    priceRub: w.priceRub,
    powerHp: w.powerHp,
    transmission: w.transmission as InventoryItem["transmission"],
    fuel: w.fuel as InventoryItem["fuel"],
    body: w.body as InventoryItem["body"],
    color: w.color,
    imageSrc: w.imageSrc || "/cars/hero-1.svg",
    featured: w.featured,
    new: w.new,
  };
}

// ─── Public API ───────────────────────────────────────────────────────────────

/** All cars. Falls back to allInventory when WP is not configured. */
export async function getCars(): Promise<InventoryItem[]> {
  const data = await wpFetch<WPCar[]>("cars");
  return data ? data.map(mapCar) : allInventory;
}

/** Featured cars only. Falls back to featuredInventory. */
export async function getFeaturedCars(): Promise<InventoryItem[]> {
  const data = await wpFetch<WPCar[]>("cars?featured=1");
  return data ? data.map(mapCar) : featuredInventory;
}

/** Customer testimonials. Falls back to static testimonials. */
export async function getTestimonials(): Promise<Testimonial[]> {
  const data = await wpFetch<WPReview[]>("reviews");
  if (!data) return staticTestimonials;
  return data.map((w) => ({
    id: w.id,
    name: w.name,
    city: w.city,
    car: w.car,
    text: w.text,
  }));
}

/** Site-wide settings (phone, email, address, hours). */
export async function getSiteSettings(): Promise<SiteSettings> {
  const data = await wpFetch<SiteSettings>("settings");
  return (
    data ?? {
      phone: "+7 (999) 000-00-00",
      email: "info@autosite.ru",
      address: "Москва, ул. Автомобильная, 1",
      hours: "Пн–Пт: 9:00–20:00, Сб–Вс: 10:00–18:00",
    }
  );
}
