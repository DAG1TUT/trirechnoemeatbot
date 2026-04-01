import { PageHero } from "@/components/site/PageHero";
import { Container } from "@/components/ui/Container";
import { SectionHeading } from "@/components/ui/SectionHeading";

export default function ServicesPage() {
  return (
    <>
      <PageHero
        kicker="Услуги"
        title="СЕРВИС ПОД КЛЮЧ"
        description="Подбор, трейд‑ин, кредит и диагностика — всё в одном месте. Страница-заглушка: дальше наполним реальными пакетами и условиями."
      />

      <section className="bg-muted py-14 sm:py-16">
        <Container>
          <SectionHeading
            kicker="Скоро"
            title="Пакеты услуг"
            description="Добавим блоки с описанием, стоимостью и формой заявки: «Подбор», «Трейд‑ин», «Кредит», «Диагностика»."
          />
        </Container>
      </section>
    </>
  );
}

