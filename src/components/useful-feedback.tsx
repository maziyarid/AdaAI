import { useState } from "react";
import { cn } from "@/lib/utils";

const REASONS = [
  { id: "unclear", label: "گام یا زبان مبهم بود" },
  { id: "wrong", label: "پیشنهاد به کارم نمی آمد" },
  { id: "need_human", label: "به مشاور انسان نیاز دارم" },
];

export function UsefulFeedback({ page }: { page: string }) {
  const [choice, setChoice] = useState<"yes" | "no" | null>(null);
  const [reason, setReason] = useState<string | null>(null);

  function save(next: "yes" | "no", why?: string) {
    setChoice(next);
    if (why) setReason(why);
    try {
      const key = "qalam-product-ux";
      const prev = JSON.parse(localStorage.getItem(key) || "[]") as unknown[];
      prev.push({ page, useful: next, reason: why ?? null, at: new Date().toISOString() });
      localStorage.setItem(key, JSON.stringify(prev.slice(-50)));
    } catch {
      /* ignore quota */
    }
  }

  return (
    <section className="rounded-[20px] bg-paper-sunken/70 p-5" aria-label="بازخورد سودمندی">
      <p className="text-sm font-medium">آیا این صفحه کارتان را جلو برد؟</p>
      <p className="mt-1 text-xs leading-6 text-ink-subtle">سیگنال محصول است نه فاکتور رتبه گوگل.</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          className={cn(
            "h-11 rounded-full px-4 text-sm",
            choice === "yes" ? "bg-ok text-paper-elevated" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
          )}
          onClick={() => save("yes")}
        >
          بله
        </button>
        <button
          type="button"
          className={cn(
            "h-11 rounded-full px-4 text-sm",
            choice === "no" ? "bg-mark text-paper-elevated" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
          )}
          onClick={() => save("no")}
        >
          خیر
        </button>
      </div>
      {choice === "no" ? (
        <div className="mt-3 flex flex-col gap-2">
          {REASONS.map((r) => (
            <button
              key={r.id}
              type="button"
              className={cn(
                "h-11 rounded-[12px] px-3 text-start text-sm",
                reason === r.id ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted",
              )}
              onClick={() => save("no", r.id)}
            >
              {r.label}
            </button>
          ))}
        </div>
      ) : null}
      {choice ? <p className="mt-3 text-sm text-ink-muted">ثبت شد. برای بهبود محصول می ماند.</p> : null}
    </section>
  );
}
