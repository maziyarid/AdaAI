import { cn } from "@/lib/utils";
import type { HTMLAttributes } from "react";

export function Badge({
  className,
  tone = "ink",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: "ink" | "slate" | "mark" | "ok" | "warn" }) {
  const tones = {
    ink: "bg-paper-sunken text-ink-muted",
    slate: "bg-slate/10 text-slate",
    mark: "bg-mark/10 text-mark",
    ok: "bg-ok/10 text-ok",
    warn: "bg-warn/12 text-warn",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
