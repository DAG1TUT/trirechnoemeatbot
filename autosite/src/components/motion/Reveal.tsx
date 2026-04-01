"use client";

import { motion, type MotionProps } from "framer-motion";
import { type ReactNode } from "react";
import { reveal as defaultReveal } from "@/lib/motion";

export function Reveal({
  children,
  className,
  ...props
}: {
  children: ReactNode;
  className?: string;
} & MotionProps) {
  return (
    <motion.div
      className={className}
      initial={defaultReveal.initial}
      whileInView={defaultReveal.whileInView}
      viewport={defaultReveal.viewport}
      transition={defaultReveal.transition}
      {...props}
    >
      {children}
    </motion.div>
  );
}

