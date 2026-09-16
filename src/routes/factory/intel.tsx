import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BRIEFING, INTEL_SOURCES, PUB_EVENTS, PUB_FINDINGS } from "@/lib/seo/data";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/factory/intel")({ component: IntelPage });

function IntelPage() {
  const [tier, setTier] = useState<number | "ALL">("ALL");
  const sources = useMemo(
    () => INTEL_SOURCES.filter((s) => (tier === "ALL" ? true : s.tier === tier)),
    [tier],
  );

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">پژوهش بیرونی · ضد نویز</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">خبر صنعت قانون کارخانه نمی شود.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          منبع اولیه حاکم است. بیست بازنویسی یک رویدادند. متن کامل مقاله ذخیره نمی شود. تیتر وارد صف تولید نمی شود.
        </p>
        <Link to="/factory/briefing" className="mt-4 inline-block">
          <Button variant="secondary">English briefing</Button>
        </Link>
      </header>

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
        <h2 className="font-display text-xl font-semibold">خلاصه این دور</h2>
        <ul className="mt-3 flex flex-col gap-2 text-sm leading-7">
          {BRIEFING.fa.changed.map((x) => (
            <li key={x}>{x}</li>
          ))}
        </ul>
        <p className="mt-3 text-sm leading-6 text-ink-muted">{BRIEFING.fa.action}</p>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">منابع</h2>
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
          {(["ALL", 0, 1, 2, 3] as const).map((t) => (
            <button
              key={String(t)}
              type="button"
              onClick={() => setTier(t)}
              className={cn(
                "h-11 shrink-0 rounded-full px-4 text-sm",
                tier === t ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
              )}
            >
              {t === "ALL" ? "همه سطح ها" : `سطح ${t}`}
            </button>
          ))}
        </div>
        <ul className="mt-4 flex flex-col gap-3">
          {sources.map((s) => (
            <li key={s.id} className="rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6">
              <div className="flex flex-wrap gap-2">
                <Badge>T{s.tier}</Badge>
                <span className="font-medium">{s.name}</span>
              </div>
              <p className="mt-1 text-ink-muted">{s.note}</p>
              <p className="mt-1 text-xs text-ink-subtle">
                آخرین بررسی {s.lastChecked} · آخرین مطلب {s.lastProcessedDate}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">خوشه رویداد</h2>
        <div className="mt-4 flex flex-col gap-4">
          {PUB_EVENTS.map((e) => (
            <article key={e.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
              <p className="font-mono text-xs text-ink-subtle">{e.id}</p>
              <h3 className="mt-1 font-display text-lg font-semibold">{e.title}</h3>
              <p className="mt-2 text-sm leading-7">{e.newEvidence}</p>
              <p className="mt-2 text-sm text-ink-muted">سؤال باز: {e.openQuestions}</p>
              <a href={e.primarySource} className="mt-2 inline-block text-sm text-slate hover:underline" target="_blank" rel="noreferrer">
                منبع اولیه
              </a>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">یافته های راستی آزمایی شده</h2>
        <div className="mt-4 flex flex-col gap-3">
          {PUB_FINDINGS.map((f) => (
            <article key={f.id} className="rounded-[20px] bg-paper-sunken/70 p-4">
              <div className="flex flex-wrap gap-2">
                <span className="font-mono text-xs">{f.id}</span>
                <Badge>{f.claimClass}</Badge>
                <Badge tone={f.urgency === "P1" || f.urgency === "P0" ? "mark" : "ink"}>{f.urgency}</Badge>
                <Badge tone="slate">{f.websiteImpact}</Badge>
              </div>
              <p className="mt-2 text-sm leading-7">{f.finding}</p>
              <p className="mt-1 text-xs leading-6 text-ink-subtle">کارخانه: {f.factoryImpact}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
