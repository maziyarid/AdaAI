import { createFileRoute, Link } from "@tanstack/react-router";
import { REGISTERS } from "@/lib/content";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/registers")({ component: RegistersPage });

function RegistersPage() {
  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">نقشه رجیستر</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          سیزده پیش تنظیم عملی. قاطی کردن مجله و کافه، یا دری و فارسی ایران، در یک بند از قوی ترین نشانه های ناهماهنگی است. عامل باید همه را بداند و یکی را انتخاب کند.
        </p>
      </header>
      <div className="grid gap-4">
        {REGISTERS.map((r) => (
          <article key={r.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="font-display text-2xl font-semibold">{r.name}</h2>
                <p className="mt-1 text-sm text-ink-muted">{r.use}</p>
              </div>
              <Link to="/desk" search={{ register: r.id }}>
                <Button size="sm" variant="secondary">
                  سنجش در این رجیستر
                </Button>
              </Link>
            </div>
            <dl className="mt-5 grid gap-3 sm:grid-cols-2">
              <Item k="رسمیت" v={r.formality} />
              <Item k="ضمیر" v={r.you} />
              <Item k="پرسش" v={r.questions} />
              <Item k="تمثیل" v={r.analogy} />
            </dl>
            <p className="mt-4 text-sm text-mark">پرهیز: {r.avoid}</p>
          </article>
        ))}
      </div>
    </main>
  );
}

function Item({ k, v }: { k: string; v: string }) {
  return (
    <div className="rounded-[12px] bg-paper-sunken/70 px-3 py-2">
      <dt className="text-xs text-ink-subtle">{k}</dt>
      <dd className="mt-0.5 text-sm leading-6">{v}</dd>
    </div>
  );
}
