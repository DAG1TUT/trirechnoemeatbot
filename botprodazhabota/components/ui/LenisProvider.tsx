'use client';

import { useLenis } from '@/hooks/useLenis';

export default function LenisProvider({ children }: { children: React.ReactNode }) {
  useLenis();
  return <>{children}</>;
}
