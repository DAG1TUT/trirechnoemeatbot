export const easeOutQuart: [number, number, number, number] = [0.22, 1, 0.36, 1];

export const reveal = {
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true as const, amount: 0.25 },
  transition: { duration: 0.55, ease: easeOutQuart },
};

