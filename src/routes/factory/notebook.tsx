import { createFileRoute } from "@tanstack/react-router";
import { LIBRARY, NOTEBOOK, TREES } from "@/lib/seo/data";

export const Route = createFileRoute("/factory/notebook")({ component: NotebookPage });

function NotebookPage() {
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">دفتر تجربه</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          مرتب بر اساس مسئله، نه کانال. هر موضوع چهار خانه دارد: انجام دهید، نکنید، مشروط، آزمایش.
        </p>
      </header>
      <div className="flex flex-col gap-8">
        {NOTEBOOK.map((block) => (
          <article key={block.topic} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
            <h2 className="font-display text-2xl font-semibold">{block.topic}</h2>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <Col title="انجام دهید" items={block.do} tone="ok" />
              <Col title="نکنید" items={block.dont} tone="mark" />
              <Col title="مشروط" items={block.depends} tone="warn" />
              <Col title="آزمایش" items={block.test} tone="slate" />
            </div>
          </article>
        ))}
      </div>
      <section>
        <h2 className="font-display text-2xl font-semibold">درخت تصمیم</h2>
        <div className="mt-4 grid gap-4">
          {TREES.map((t) => (
            <article key={t.id} className="rounded-[20px] bg-paper-sunken/70 p-5">
              <h3 className="font-display text-lg font-semibold">{t.title}</h3>
              <ol className="mt-3 flex flex-col gap-2">
                {t.steps.map((s, i) => (
                  <li key={s} className="flex gap-3 text-sm leading-6">
                    <span className="font-mono text-xs text-ink-subtle">{String(i + 1).padStart(2, "0")}</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ol>
            </article>
          ))}
        </div>
      </section>
      <section>
        <h2 className="font-display text-2xl font-semibold">ورود کتابخانه پژوهش</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-ink-muted">
          فقط سنتز قابل استفاده مجدد. پست تلگرام خام اینجا نیست. وضعیت باطل شده حذف نمی شود.
        </p>
        <ul className="mt-4 flex flex-col gap-3">
          {LIBRARY.map((x) => (
            <li key={x.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <p className="font-mono text-xs text-ink-subtle">
                {x.id} · {x.status} · {x.evidenceKind}
              </p>
              <p className="mt-2 font-medium">{x.topic}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{x.claim}</p>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

function Col({ title, items, tone }: { title: string; items: string[]; tone: "ok" | "mark" | "warn" | "slate" }) {
  const border = {
    ok: "border-ok/25",
    mark: "border-mark/25",
    warn: "border-warn/30",
    slate: "border-rule",
  }[tone];
  if (!items.length) {
    return (
      <div className={`rounded-[16px] border ${border} p-4`}>
        <p className="text-xs text-ink-subtle">{title}</p>
        <p className="mt-2 text-sm text-ink-subtle">خالی — هنوز شاهد تکراری نداریم.</p>
      </div>
    );
  }
  return (
    <div className={`rounded-[16px] border ${border} p-4`}>
      <p className="text-xs text-ink-subtle">{title}</p>
      <ul className="mt-2 flex flex-col gap-2">
        {items.map((x) => (
          <li key={x} className="text-sm leading-6">
            {x}
          </li>
        ))}
      </ul>
    </div>
  );
}
