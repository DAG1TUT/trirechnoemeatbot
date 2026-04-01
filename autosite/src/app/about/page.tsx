import { PageHero } from "@/components/site/PageHero";
import { Container } from "@/components/ui/Container";
import { SectionHeading } from "@/components/ui/SectionHeading";

export default function AboutPage() {
  return (
    <>
      <PageHero
        kicker="О компании"
        title="ДОВЕРИЕ. СКОРОСТЬ. КАЧЕСТВО."
        description="Мы работаем на рынке много лет и выстроили процесс так, чтобы вы получали автомобиль без лишних рисков и потерь времени."
      />

      <section className="bg-muted py-14 sm:py-16">
        <Container>
          <SectionHeading
            kicker="Скоро"
            title="История и гарантии"
            description="Сюда добавим конкретные цифры, команду, партнёров и блок гарантий — чтобы закрыть все вопросы до покупки."
          />
        </Container>
      </section>
    </>
  );
}

