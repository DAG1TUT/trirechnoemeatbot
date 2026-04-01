import { type ReactNode } from "react";

export function SectionHeading({
  kicker,
  title,
  description,
  align = "left",
}: {
  kicker?: ReactNode;
  title: ReactNode;
  description?: ReactNode;
  align?: "left" | "center";
}) {
  const isCenter = align === "center";

  return (
    <div className={isCenter ? "text-center" : "text-left"}>
      {kicker ? (
        <div
          className={`inline-flex items-center gap-2 ${
            isCenter ? "justify-center" : "justify-start"
          }`}
        >
          <span className="inline-block h-1.5 w-8 bg-accent [clip-path:polygon(10%_0%,100%_0%,90%_100%,0%_100%)]" />
          <span className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-600">
            {kicker}
          </span>
        </div>
      ) : null}

      <h2 className="mt-3 text-2xl font-black uppercase tracking-tight text-navy sm:text-3xl">
        {title}
      </h2>

      {description ? (
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base sm:leading-7">
          {description}
        </p>
      ) : null}
    </div>
  );
}

