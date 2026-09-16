import { createFileRoute } from "@tanstack/react-router";
import { BIBLE } from "@/lib/content";

export const Route = createFileRoute("/bible")({ component: BiblePage });

function BiblePage() {
  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">کتابچه نگارش</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          استاندارد زنده برای عامل های نگارش. سبک هیچ وقت حقیقت را باطل نمی کند. نسخه کامل مهارتی در مخزن مهارت است؛ اینجا ستون فقرات اجرایی است.
        </p>
      </header>
      <div className="flex flex-col gap-4">
        {BIBLE.map((s) => (
          <article key={s.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
            <h2 className="font-display text-xl font-semibold">{s.title}</h2>
            <p className="mt-3 leading-8 text-ink-muted">{s.body}</p>
          </article>
        ))}
      </div>
    </main>
  );
}
