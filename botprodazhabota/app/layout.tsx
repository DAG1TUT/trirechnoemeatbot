import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.scss'
import LenisProvider from '@/components/ui/LenisProvider'

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] })
const geistMono = Geist_Mono({ variable: '--font-geist-mono', subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Блик — живой продавец в VK',
  description: 'AI-ассистент для автоматизации продаж в VK Сообщениях',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <div className="caustics">
          {/* Blob 1 — warm gold top-left */}
          <div
            style={{
              position: 'absolute',
              width: '520px',
              height: '520px',
              top: '-80px',
              left: '-120px',
              background: 'radial-gradient(circle, rgba(245,200,80,0.60) 0%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'caustic1 18s ease-in-out infinite',
            }}
          />
          {/* Blob 2 — cool blue right */}
          <div
            style={{
              position: 'absolute',
              width: '440px',
              height: '440px',
              top: '25%',
              right: '-80px',
              background: 'radial-gradient(circle, rgba(180,220,255,0.45) 0%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'caustic2 22s ease-in-out infinite',
            }}
          />
          {/* Blob 3 — amber gold bottom-center */}
          <div
            style={{
              position: 'absolute',
              width: '500px',
              height: '340px',
              bottom: '12%',
              left: '18%',
              background: 'radial-gradient(ellipse, rgba(245,158,11,0.28) 0%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'caustic3 27s ease-in-out infinite',
            }}
          />
          {/* Blob 4 — lavender bottom-right */}
          <div
            style={{
              position: 'absolute',
              width: '400px',
              height: '400px',
              bottom: '-60px',
              right: '12%',
              background: 'radial-gradient(circle, rgba(220,200,255,0.32) 0%, transparent 70%)',
              backgroundSize: '200% 200%',
              animation: 'caustic4 31s ease-in-out infinite',
            }}
          />
        </div>
        <LenisProvider>
          {children}
        </LenisProvider>
      </body>
    </html>
  )
}
