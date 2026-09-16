import { createFileRoute } from "@tanstack/react-router";
import { CORPUS } from "@/lib/content";

export const Route = createFileRoute("/corpus")({ component: CorpusPage });

function CorpusPage() {
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">{CORPUS.headline}</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          کافه فلسفه لنگر مکانیک نثر فکری معاصر ایرانی است. نقل هایدگر، فروید، ابن عربی و شکسپیر شاهد ساخت جمله نویسندگان کانال نیست. تکیه کلام هیچ مشارکت کننده ای الگو نمی شود.
        </p>
      </header>

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {CORPUS.facts.map((f) => (
          <div key={f.k} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
            <p className="font-display text-2xl font-semibold tabular-nums">{f.v}</p>
            <p className="mt-1 text-xs leading-5 text-ink-muted">{f.k}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        {CORPUS.layers.map((l) => (
          <article key={l.t} className="rounded-[20px] bg-paper-sunken/70 p-5">
            <h2 className="font-display text-xl font-semibold">{l.t}</h2>
            <p className="mt-2 leading-7 text-ink-muted">{l.d}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div>
          <h2 className="font-display text-2xl font-semibold">قابل انتقال</h2>
          <ol className="mt-4 flex flex-col gap-2">
            {CORPUS.transferable.map((t, i) => (
              <li key={t} className="flex gap-3 text-sm leading-6">
                <span className="font-mono text-xs text-ink-subtle">{String(i + 1).padStart(2, "0")}</span>
                <span>{t}</span>
              </li>
            ))}
          </ol>
        </div>
        <div>
          <h2 className="font-display text-2xl font-semibold">کپی نکنید</h2>
          <ul className="mt-4 flex flex-col gap-2">
            {CORPUS.forbidden.map((t) => (
              <li key={t} className="rounded-[12px] bg-mark/8 px-3 py-2 text-sm leading-6 text-mark">
                {t}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
