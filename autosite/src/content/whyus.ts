import {
  BadgeCheck,
  Car,
  CreditCard,
  ShieldCheck,
  Wrench,
} from "lucide-react";

export type WhyUsItem = {
  id: string;
  title: string;
  text: string;
  Icon: typeof Car;
};

export const whyUs: WhyUsItem[] = [
  {
    id: "w1",
    title: "Проверенная история",
    text: "Юридическая чистота, отчёты и прозрачные условия — без сюрпризов после покупки.",
    Icon: ShieldCheck,
  },
  {
    id: "w2",
    title: "Диагностика 360°",
    text: "Техническая проверка, кузов, электрика и тест‑драйв перед выдачей.",
    Icon: Wrench,
  },
  {
    id: "w3",
    title: "Гарантия качества",
    text: "Сертифицированная предпродажная подготовка и контроль состояния.",
    Icon: BadgeCheck,
  },
  {
    id: "w4",
    title: "Гибкая оплата",
    text: "Кредит, трейд‑ин и быстрые способы оплаты. Подберём комфортный сценарий.",
    Icon: CreditCard,
  },
  {
    id: "w5",
    title: "Подбор под вас",
    text: "Соберём предложения под бюджет и задачи, предложим 3–5 лучших вариантов.",
    Icon: Car,
  },
];

