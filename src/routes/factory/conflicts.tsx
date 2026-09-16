import { createFileRoute } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { CHANGELOG, CONFLICTS, REJECTS } from "@/lib/seo/data";

export const Route = createFileRoute("/factory/conflicts")({ component: ConflictsPage });

function ConflictsPage() {
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">ماتریس تعارض</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          دو ادعای متضاد را میانگین نمی کنیم. شرط، شاهد، و کار فعلی کارخانه را جدا نگه می داریم. تغییر عقیده همان نویسنده در طول زمان هم اینجاست.
        </p>
      </header>
      <div className="flex flex-col gap-5">
        {CONFLICTS.map((c) => (
          <article key={c.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
            <p className="font-mono text-xs text-ink-subtle">{c.id}</p>
            <h2 className="mt-1 font-display text-xl font-semibold">{c.title}</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <p className="rounded-[16px] bg-paper-sunken/80 p-4 text-sm leading-7">{c.a}</p>
              <p className="rounded-[16px] bg-paper-sunken/80 p-4 text-sm leading-7">{c.b}</p>
            </div>
            <dl className="mt-4 grid gap-3 text-sm leading-6 sm:grid-cols-2">
              <div>
                <dt className="text-xs text-ink-subtle">کی الف</dt>
                <dd className="mt-1 text-ink-muted">{c.whenA}</dd>
              </div>
              <div>
                <dt className="text-xs text-ink-subtle">کی ب</dt>
                <dd className="mt-1 text-ink-muted">{c.whenB}</dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-xs text-ink-subtle">شاهد</dt>
                <dd className="mt-1 text-ink-muted">{c.evidence}</dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-xs text-ink-subtle">کارخانه الان</dt>
                <dd className="mt-1">{c.factoryNow}</dd>
              </div>
            </dl>
            {c.test ? <p className="mt-3 text-sm text-ink-muted">آزمایش: {c.test}</p> : null}
          </article>
        ))}
      </div>

      <section>
        <h2 className="font-display text-2xl font-semibold">دفتر نپذیرید</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-ink-muted">
          ادعا ارزیابی می شود نه گوینده. تاکتیک خطرناک، منسوخ، یا بیش تعمیم اینجا می ماند تا دوباره وارد خط تولید نشود.
        </p>
        <ul className="mt-4 flex flex-col gap-3">
          {REJECTS.map((r) => (
            <li key={r.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="mark">رد</Badge>
                <span className="font-mono text-xs text-ink-subtle">{r.id}</span>
              </div>
              <p className="mt-2 font-medium">{r.title}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{r.why}</p>
              <p className="mt-2 text-xs text-ink-subtle">{r.sources.join(" ")}</p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">تغییرات کارخانه</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-ink-muted">
          شیت زنده بیرون این پیش نمایش است. بندهای زیر پیشنهاد افزودنی اند؛ تاریخچه پژوهش موجود پاک نمی شود.
        </p>
        <ul className="mt-4 flex flex-col gap-3">
          {CHANGELOG.map((x) => (
            <li key={x.tab} className="rounded-[20px] bg-paper-sunken/70 p-4 text-sm leading-7">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={x.additive ? "ok" : "warn"}>{x.additive ? "افزودنی" : "جایگزین"}</Badge>
                <span className="text-xs text-ink-subtle">{x.at}</span>
              </div>
              <p className="mt-2 font-medium">{x.tab}</p>
              <p className="mt-1 text-ink-muted">قبل: {x.old}</p>
              <p className="mt-1">{x.now}</p>
              <p className="mt-2 text-xs text-ink-subtle">
                دلیل: {x.reason} · منبع: {x.sources.join(" ")}
              </p>
              <p className="mt-1 text-xs text-ink-subtle">بازگشت: {x.rollback}</p>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
