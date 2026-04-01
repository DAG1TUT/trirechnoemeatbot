"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { type ReactNode } from "react";

type Props = {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  variant?: "accent" | "navy" | "ghost";
  size?: "sm" | "md" | "lg";
  className?: string;
  ariaLabel?: string;
};

const sizes: Record<NonNullable<Props["size"]>, string> = {
  sm: "h-10 px-4 text-sm",
  md: "h-12 px-5 text-sm sm:text-base",
  lg: "h-14 px-6 text-base sm:text-lg",
};

const variants: Record<NonNullable<Props["variant"]>, string> = {
  accent: "bg-accent text-white",
  navy: "bg-navy text-white",
  ghost: "bg-white/0 text-navy ring-1 ring-inset ring-navy/20 hover:ring-navy/35",
};

function Inner({
  children,
  variant = "accent",
  size = "md",
  className = "",
}: Omit<Props, "href" | "onClick">) {
  const base =
    "group relative inline-flex items-center justify-center overflow-hidden select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-white";

  return (
    <motion.span
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      className={[
        base,
        sizes[size],
        variants[variant],
        "skew-x-[-12deg] [clip-path:polygon(6%_0%,100%_0%,94%_100%,0%_100%)]",
        className,
      ].join(" ")}
    >
      <motion.span
        aria-hidden
        initial={{ scaleX: 0 }}
        whileHover={{ scaleX: 1 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        className={[
          "absolute inset-0 origin-left",
          variant === "ghost"
            ? "bg-accent/10"
            : "bg-white/10 mix-blend-overlay",
        ].join(" ")}
        style={{ transformOrigin: "0% 50%" }}
      />

      <span className="relative skew-x-[12deg] font-bold uppercase tracking-wide">
        {children}
      </span>
    </motion.span>
  );
}

export function SlantedButton(props: Props) {
  if (props.href) {
    return (
      <Link
        href={props.href}
        className="inline-flex"
        aria-label={props.ariaLabel}
      >
        <Inner {...props} />
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={props.onClick}
      className="inline-flex"
      aria-label={props.ariaLabel}
    >
      <Inner {...props} />
    </button>
  );
}

