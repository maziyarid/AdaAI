import { createFileRoute } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { ACTIONS, COVERAGE, EXPERIMENTS, OPPORTUNITIES, SITES } from "@/lib/seo/data";

export const Route = createFileRoute("/factory/queue")({ component: QueuePage });

function QueuePage() {
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">صف اقدام و آزمایش</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          هیچ آزمایش سایت وایید. همگروه محدود، متریک، و مسیر بازگشت. یافته تلگرام به خودی خود صفحه تازه نمی سازد.
        </p>
      </header>

      <section>
        <h2 className="font-display text-2xl font-semibold">اقدام ها</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {ACTIONS.map((a) => (
            <li key={a.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={a.priority === "P0" ? "mark" : a.priority === "P1" ? "warn" : "slate"}>{a.priority}</Badge>
                <span className="font-mono text-xs text-ink-subtle">{a.id}</span>
              </div>
              <p className="mt-2 font-medium">{a.title}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{a.why}</p>
              <p className="mt-2 text-xs text-ink-subtle">
                {a.owner} · {a.sources.join(" ")}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">فرصت سایت</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {OPPORTUNITIES.map((o) => (
            <li key={o.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={o.priority === "P0" ? "mark" : o.priority === "P4" ? "ink" : "slate"}>{o.priority}</Badge>
                <Badge>{o.kind}</Badge>
                <span className="font-mono text-xs text-ink-subtle">{o.id}</span>
              </div>
              <p className="mt-2 font-medium">{o.target}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{o.action}</p>
              <p className="mt-2 text-xs text-ink-subtle">
                {o.site} · {o.intent} · {o.sources.join(" ")}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">آزمایش ها</h2>
        <div className="mt-4 flex flex-col gap-4">
          {EXPERIMENTS.map((e) => (
            <article key={e.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap gap-2">
                <span className="font-mono text-xs text-ink-subtle">{e.id}</span>
                <Badge tone={e.status === "rejected" ? "mark" : e.status === "ready_for_review" ? "ok" : "slate"}>
                  {e.status === "rejected" ? "رد شده" : e.status === "ready_for_review" ? "آماده بازبینی" : "صف"}
                </Badge>
              </div>
              <h3 className="mt-2 font-display text-lg font-semibold">{e.hypothesis}</h3>
              <dl className="mt-3 grid gap-2 text-sm leading-6 sm:grid-cols-2">
                <KV k="محدوده" v={e.scope} />
                <KV k="متغیر" v={e.variable} />
                <KV k="کنترل" v={e.control} />
                <KV k="متریک اصلی" v={e.primary} />
                <KV k="پنجره" v={e.window} />
                <KV k="بازگشت" v={e.rollback} />
              </dl>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">نمایه و پوشش</h2>
        <div className="mt-4 grid gap-3">
          {SITES.map((s) => (
            <div key={s.id} className="rounded-[20px] bg-paper-sunken/70 p-4 text-sm leading-7">
              <p className="font-medium">{s.domain}</p>
              <p className="mt-1 text-ink-muted">{s.notes}</p>
              <ul className="mt-2">
                {s.serviceOwners.map((o) => (
                  <li key={o.url}>
                    {o.intent}: {o.url}
                  </li>
                ))}
              </ul>
            </div>
          ))}
          {COVERAGE.sources.map((s) => (
            <div key={s.id} className="rounded-[20px] bg-paper-elevated p-4 text-sm leading-6 shadow-[var(--shadow-border)]">
              <p className="font-medium">{s.id}</p>
              <p className="text-ink-muted">
                {s.earliest ?? "—"} تا {s.latest ?? "—"} · {s.inspected} پیام · ویدئو {s.videos}
              </p>
              <p className="mt-1 text-ink-muted">{s.inaccessible}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function KV({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-subtle">{k}</dt>
      <dd className="text-ink-muted">{v}</dd>
    </div>
  );
}
