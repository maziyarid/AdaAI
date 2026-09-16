import { createFileRoute, Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  A11Y,
  EXPERIENCE_NOTES,
  FEEDBACK_EVENTS,
  INTERACTIVE_ASSETS,
  MULTIMEDIA_GAPS,
  PERFORMANCE_RULES,
  UX_SURFACES,
} from "@/lib/seo/data";

export const Route = createFileRoute("/factory/ux")({ component: UxPage });

function UxPage() {
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">تجربه · دسترسی · ابزار</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">زبان رابط هم قلم است.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          دکمه باید کار را بگوید. ویجت فقط اگر تصمیمی را جلو ببرد. دسترسی بخشی از سودمندی است نه تزئین.
        </p>
      </header>

      <section>
        <h2 className="font-display text-2xl font-semibold">زبان سطوح</h2>
        <div className="mt-4 flex flex-col gap-3">
          {UX_SURFACES.map((u) => (
            <article key={u.id} className="grid gap-3 rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)] md:grid-cols-2">
              <div>
                <p className="text-xs text-ink-subtle">{u.surface}</p>
                <p className="mt-1 text-sm text-mark">{u.bad}</p>
              </div>
              <div>
                <p className="text-sm">{u.better}</p>
                <p className="mt-1 text-xs leading-6 text-ink-muted">{u.why}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h2 className="font-display text-2xl font-semibold">ابزارهای تصمیم</h2>
          <div className="flex gap-2">
            <Link to="/tools/stat-test">
              <Button size="sm">انتخاب آزمون</Button>
            </Link>
            <Link to="/tools/feasibility">
              <Button size="sm" variant="secondary">
                امکان سنجی
              </Button>
            </Link>
            <Link to="/tools/questionnaire">
              <Button size="sm" variant="secondary">
                پرسشنامه
              </Button>
            </Link>
            <Link to="/tools/defence">
              <Button size="sm" variant="secondary">
                آمادگی دفاع
              </Button>
            </Link>
          </div>
        </div>
        <div className="mt-4 flex flex-col gap-3">
          {INTERACTIVE_ASSETS.map((a) => (
            <article key={a.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap gap-2">
                <span className="font-mono text-xs text-ink-subtle">{a.id}</span>
                <Badge>{a.status}</Badge>
              </div>
              <h3 className="mt-2 font-display text-lg font-semibold">{a.name}</h3>
              <p className="mt-1 text-sm leading-7">{a.userJob}</p>
              <p className="mt-2 text-sm leading-6 text-ink-muted">حد: {a.limitations}</p>
              <p className="mt-1 text-sm text-ink-subtle">مالک کانونی: {a.canonicalOwner}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">دسترسی</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {A11Y.map((a) => (
            <li key={a.id} className="rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6">
              <Badge tone={a.status === "fixed_here" ? "ok" : "warn"}>{a.status}</Badge>
              <p className="mt-2 font-medium">{a.where}</p>
              <p className="text-ink-muted">{a.issue}</p>
              <p className="text-ink-muted">{a.fix}</p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">تجربه دست اول</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
          حکایت یک پرونده قانون نمی شود. داده خصوصی دانشجو اینجا نیست.
        </p>
        <div className="mt-4 flex flex-col gap-3">
          {EXPERIENCE_NOTES.map((x) => (
            <article key={x.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <Badge>{x.kind}</Badge>
              <h3 className="mt-2 font-medium">{x.topic}</h3>
              <p className="mt-1 text-sm leading-7 text-ink-muted">{x.observation}</p>
              <p className="mt-2 text-xs text-ink-subtle">به این ارتقا ندهید: {x.cannotPromoteTo}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">بازخورد محصول</h2>
        <ul className="mt-3 flex flex-col gap-2 text-sm leading-6 text-ink-muted">
          {FEEDBACK_EVENTS.map((e) => (
            <li key={e.id}>
              <span className="font-mono text-xs">{e.id}</span> — {e.meaning} ({e.source})
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">عملکرد و رسانه</h2>
        <ul className="mt-3 flex flex-col gap-2 text-sm leading-6">
          {PERFORMANCE_RULES.map((r) => (
            <li key={r} className="rounded-[12px] bg-paper-sunken/70 px-4 py-3">
              {r}
            </li>
          ))}
        </ul>
        <div className="mt-4 flex flex-col gap-3">
          {MULTIMEDIA_GAPS.map((m) => (
            <article key={m.url} className="rounded-[16px] bg-paper-elevated p-4 text-sm leading-6 shadow-[var(--shadow-border)]">
              <p className="text-ink-subtle">{m.url}</p>
              <p className="mt-1">{m.opportunity}</p>
              <p className="text-ink-muted">نه: {m.not}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
