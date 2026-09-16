import type { TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-48 w-full resize-y rounded-[16px] bg-paper-elevated px-4 py-3 text-base leading-7 text-ink",
        "shadow-[var(--shadow-border)] placeholder:text-ink-subtle",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate/35",
        className,
      )}
      {...props}
    />
  );
}
