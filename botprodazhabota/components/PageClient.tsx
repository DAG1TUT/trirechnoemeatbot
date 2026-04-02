'use client';

import { useState } from 'react';
import Navbar from '@/components/sections/Navbar';
import Hero from '@/components/sections/Hero';
import Features from '@/components/sections/Features';
import SystemPromptConfig from '@/components/sections/SystemPromptConfig';
import Pricing from '@/components/sections/Pricing';
import CTASection from '@/components/sections/CTASection';
import Footer from '@/components/sections/Footer';

export default function PageClient() {
  const [sysPrompt, setSysPrompt] = useState('');

  return (
    <main>
      <Navbar />
      <Hero systemPrompt={sysPrompt} />
      <SystemPromptConfig onApply={setSysPrompt} />
      <Features />
      <Pricing />
      <CTASection />
      <Footer />
    </main>
  );
}
