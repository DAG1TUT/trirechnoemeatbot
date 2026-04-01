import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        navy: "#001D3D",
        accent: "#FF6B00",
        muted: "#F4F4F4",
      },
    },
  },
  plugins: [],
} satisfies Config;

