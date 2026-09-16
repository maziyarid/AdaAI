import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { FINDINGS } from "@/lib/seo/data";
import type { Currency, Stance } from "@/lib/seo/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/factory/corpus")({ component: CorpusPage });

const STANCE: Record<Stance, { label: string; tone: "ok" | "mark" | "warn" | "slate" }> = {
  DO: { label: "انجام دهید", tone: "ok" },
  DONT: { label: "نکنید", tone: "mark" },
  DEPENDS: { label: "مشروط", tone: "warn" },
  TEST: { label: "آزمایش", tone: "slate" },
};

const CURRENCY: Record<Currency, string> = {
  CURRENT: "جاری",
  CURRENT_BUT_CONTEXTUAL: "جاری مشروط",
  NEEDS_REVALIDATION: "نیاز به بازآزمایی",
  HISTORICAL_ONLY: "فقط تاریخی",
  SUPERSEDED: "باطل شده",
};

function CorpusPage() {
  const [q, setQ] = useState("");
  const [stance, setStance] = useState<Stance | "ALL">("ALL");
  const [topic, setTopic] = useState("ALL");
  const topics = useMemo(() => Array.from(new Set(FINDINGS.map((f) => f.topic))), []);
  const items = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return FINDINGS.filter((f) => {
      if (stance !== "ALL" && f.stance !== stance) return false;
      if (topic !== "ALL" && f.topic !== topic) return false;
      if (!needle) return true;
      const blob = [f.id, f.topic, f.subtopic, f.normalised, f.observation, f.factory, f.source, f.author]
        .join(" ")
        .toLowerCase();
      return blob.includes(needle);
    });
  }, [q, stance, topic]);

  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">پیکره میدانی سئو</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          نقل ساخت یافته، نه بازنشر کانال. نثر منبع کپی نمی شود. اعتماد بر اساس سند است نه شهرت گوینده.
        </p>
      </header>
      <div className="flex flex-col gap-3">
        <label className="sr-only" htmlFor="corpus-search">
          جستجوی پیکره
        </label>
        <input
          id="corpus-search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="جستجو: ایندکس، تازه سازی، برخورد نیت، رپورتاژ…"
          className="h-12 rounded-[14px] border-0 bg-paper-elevated px-4 text-sm shadow-[var(--shadow-border)] outline-none focus:shadow-[var(--shadow-border-hover)]"
        />
        <div className="flex gap-2 overflow-x-auto pb-1">
          {(["ALL", "DO", "DONT", "DEPENDS", "TEST"] as const).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setStance(s)}
              className={cn(
                "h-11 shrink-0 rounded-full px-4 text-sm",
                stance === s ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
              )}
            >
              {s === "ALL" ? "همه موضع ها" : STANCE[s].label}
            </button>
          ))}
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1">
          <button
            type="button"
            onClick={() => setTopic("ALL")}
            className={cn(
              "h-11 shrink-0 rounded-full px-4 text-sm",
              topic === "ALL" ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
            )}
          >
            همه موضوع ها
          </button>
          {topics.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTopic(t)}
              className={cn(
                "h-11 shrink-0 rounded-full px-4 text-sm",
                topic === t ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>
      <p className="text-sm text-ink-subtle">{items.length} یافته</p>
      {items.length === 0 ? (
        <p className="rounded-[20px] bg-paper-sunken/70 p-5 text-sm leading-7 text-ink-muted">
          چیزی با این صافی پیدا نشد. موضوع یا موضع را عوض کنید.
        </p>
      ) : null}
      <div className="flex flex-col gap-4">
        {items.map((f) => (
          <article key={f.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs text-ink-subtle">{f.id}</span>
              <Badge tone={STANCE[f.stance].tone}>{STANCE[f.stance].label}</Badge>
              <Badge>{CURRENCY[f.currency]}</Badge>
              <Badge tone="slate">{f.confidence}</Badge>
            </div>
            <h2 className="mt-3 font-display text-xl font-semibold">
              {f.topic} · {f.subtopic}
            </h2>
            <p className="mt-2 leading-7">{f.normalised}</p>
            <p className="mt-3 text-sm leading-7 text-ink-muted">{f.observation}</p>
            <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
              <Row k="شرط" v={f.conditions} />
              <Row k="کارخانه" v={f.factory} />
              <Row k="ریسک" v={f.risk} />
              <Row k="منبع" v={`${f.source} · ${f.date}`} />
            </dl>
            {f.url ? (
              <a href={f.url} className="mt-3 inline-block text-sm text-slate hover:underline" target="_blank" rel="noreferrer">
                سند منبع
              </a>
            ) : null}
          </article>
        ))}
      </div>
    </main>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-subtle">{k}</dt>
      <dd className="mt-0.5 leading-6 text-ink-muted">{v}</dd>
    </div>
  );
}
