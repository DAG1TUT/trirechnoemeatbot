export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <style>{`
          *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
          body { font-family: 'Inter', system-ui, sans-serif; background: #0f0f13; color: #e8e8f0; }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
