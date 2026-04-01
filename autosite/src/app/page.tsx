import { FeaturedInventory } from "@/components/site/FeaturedInventory";
import { HeroSlider } from "@/components/site/HeroSlider";
import { StatsBlock } from "@/components/site/StatsBlock";
import { TestimonialsSlider } from "@/components/site/TestimonialsSlider";
import { WhyUs } from "@/components/site/WhyUs";
import { getFeaturedCars, getTestimonials } from "@/lib/wp";

export const revalidate = 60;

export default async function Home() {
  const [featuredCars, testimonials] = await Promise.all([
    getFeaturedCars(),
    getTestimonials(),
  ]);

  return (
    <>
      <HeroSlider />
      <FeaturedInventory cars={featuredCars} />
      <StatsBlock />
      <WhyUs />
      <TestimonialsSlider testimonials={testimonials} />
    </>
  );
}
