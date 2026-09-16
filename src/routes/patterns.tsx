import { createFileRoute } from "@tanstack/react-router";
import { PATTERNS } from "@/lib/content";

export const Route = createFileRoute("/patterns")({ component: PatternsPage });

function PatternsPage() {
  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">بانک حرکت</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          مکانیک را یاد بگیرید، امضا را نه. مثال ها نو ساخته شده اند و موضوعشان پژوهش است، نه فلسفه کافه.
        </p>
      </header>
      <div className="flex flex-col gap-5">
        {PATTERNS.map((p) => (
          <article key={p.id} className="overflow-hidden rounded-[24px] bg-paper-elevated shadow-[var(--shadow-border)]">
            <div className="border-b border-rule px-5 py-3 sm:px-6">
              <p className="text-sm font-medium text-slate">
                {p.id} · {p.move}
              </p>
            </div>
            <div className="grid gap-0 md:grid-cols-2">
              <Block label="پیش" text={p.before} weak />
              <Block label="پس" text={p.after} />
            </div>
            <p className="px-5 py-3 text-sm leading-6 text-ink-muted sm:px-6">{p.why}</p>
          </article>
        ))}
      </div>
    </main>
  );
}

function Block({ label, text, weak }: { label: string; text: string; weak?: boolean }) {
  return (
    <div className={weak ? "bg-paper-sunken/50 px-5 py-4 sm:px-6" : "px-5 py-4 sm:px-6"}>
      <p className="text-xs text-ink-subtle">{label}</p>
      <p className="mt-2 leading-7">{text}</p>
    </div>
  );
}
