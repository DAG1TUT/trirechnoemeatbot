import { CatalogClient } from "@/components/catalog/CatalogClient";
import { PageHero } from "@/components/site/PageHero";
import { getCars } from "@/lib/wp";

export const revalidate = 60;

export default async function CatalogPage() {
  const cars = await getCars();

  return (
    <>
      <PageHero
        kicker="Каталог"
        title="АВТОМОБИЛИ В НАЛИЧИИ"
        description={`${cars.length} автомобилей с честной диагностикой и прозрачными условиями покупки.`}
      />
      <CatalogClient cars={cars} />
    </>
  );
}
