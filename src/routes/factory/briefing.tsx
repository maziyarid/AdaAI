import { createFileRoute, Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { BRIEFING, SIGNAL_POLICY } from "@/lib/seo/data";

export const Route = createFileRoute("/factory/briefing")({ component: BriefingPage });

function BriefingPage() {
  const b = BRIEFING.en;
  return (
    <main className="flex flex-col gap-8 text-left" lang="en" dir="ltr">
      <header className="max-w-2xl">
        <Badge tone="slate">Periodic briefing</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">What changed, and what we will not do.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          Humans stay the audience. Generative search is a discovery surface. This page is English on purpose so an
          operator can brief without translating folklore.
        </p>
      </header>
      <section>
        <h2 className="font-display text-2xl font-semibold">What changed</h2>
        <ul className="mt-3 flex flex-col gap-2 text-sm leading-7">
          {b.changed.map((x) => (
            <li key={x} className="rounded-[16px] bg-paper-sunken/70 px-4 py-3">
              {x}
            </li>
          ))}
        </ul>
      </section>
      <section className="grid gap-3 md:grid-cols-2">
        <article className="rounded-[20px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <h3 className="font-medium">Why it matters</h3>
          <p className="mt-2 text-sm leading-7 text-ink-muted">{b.why}</p>
        </article>
        <article className="rounded-[20px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <h3 className="font-medium">Evidence quality</h3>
          <p className="mt-2 text-sm leading-7 text-ink-muted">{b.evidence}</p>
        </article>
        <article className="rounded-[20px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <h3 className="font-medium">Our sites</h3>
          <p className="mt-2 text-sm leading-7 text-ink-muted">{b.sites}</p>
        </article>
        <article className="rounded-[20px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <h3 className="font-medium">Action / test / ignore</h3>
          <p className="mt-2 text-sm leading-7 text-ink-muted">{b.action}</p>
        </article>
      </section>
      <section>
        <h2 className="font-display text-2xl font-semibold">Signal sources stay separate</h2>
        <ul className="mt-3 flex flex-col gap-2 text-sm leading-6">
          {SIGNAL_POLICY.map((s) => (
            <li key={s.source} className="rounded-[12px] bg-paper-sunken/70 px-4 py-3">
              <span className="font-mono text-xs">{s.source}</span> — {s.use}
            </li>
          ))}
        </ul>
      </section>
      <p className="text-sm">
        <Link to="/factory/intel" className="text-slate hover:underline">
          Back to the Persian intel desk
        </Link>
      </p>
    </main>
  );
}
