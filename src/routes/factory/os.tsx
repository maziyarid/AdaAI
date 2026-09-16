import { createFileRoute, Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  CALCULATOR_CHILDREN,
  DELIVERABLE,
  OS_GAPS,
  OS_STATE,
  TECHNIQUES,
  VALIDATION,
} from "@/lib/seo/data";
import type { GapDisposition } from "@/lib/seo/types";

export const Route = createFileRoute("/factory/os")({ component: OsPage });

const TONE: Record<GapDisposition, "ok" | "warn" | "slate" | "mark"> = {
  fixed_here: "ok",
  queued: "warn",
  accepted: "slate",
  blocked: "mark",
};

const LABEL: Record<GapDisposition, string> = {
  fixed_here: "بسته در این جعبه ابزار",
  queued: "صف با مالک",
  accepted: "آگاهانه پذیرفته",
  blocked: "مسدود بیرونی",
};

function OsPage() {
  const counts = {
    fixed_here: OS_GAPS.filter((g) => g.disposition === "fixed_here").length,
    queued: OS_GAPS.filter((g) => g.disposition === "queued").length,
    accepted: OS_GAPS.filter((g) => g.disposition === "accepted").length,
    blocked: OS_GAPS.filter((g) => g.disposition === "blocked").length,
  };

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="ok">{OS_STATE.label}</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">شکاف خاموش نمی ماند.</h1>
        <p className="mt-3 leading-7 text-ink-muted">{OS_STATE.meaning}</p>
        <p className="mt-2 text-sm text-ink-subtle">تا {OS_STATE.asOf}. سایت زنده بازنویسی نشد.</p>
      </header>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {(
          [
            ["بسته اینجا", counts.fixed_here],
            ["صف", counts.queued],
            ["پذیرفته", counts.accepted],
            ["مسدود", counts.blocked],
          ] as const
        ).map(([k, v]) => (
          <div key={k} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
            <p className="font-display text-2xl font-semibold">{v}</p>
            <p className="mt-1 text-xs text-ink-muted">{k}</p>
          </div>
        ))}
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">رجیستر شکاف</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {OS_GAPS.map((g) => (
            <li key={g.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs text-ink-subtle">{g.id}</span>
                <Badge tone={TONE[g.disposition]}>{LABEL[g.disposition]}</Badge>
                <span className="text-xs text-ink-subtle">{g.area}</span>
              </div>
              <p className="mt-2 text-sm leading-7">{g.gap}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{g.next}</p>
              <p className="mt-1 text-xs text-ink-subtle">{g.owner}</p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">اعتبارسنجی نوع صفحه</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
          راهنما، خدمات، ابزار، دانلود، انگلیسی، فارسی، و یک صفحه با روش دست اول. نمره واحد نیست.
        </p>
        <div className="mt-4 flex flex-col gap-3">
          {VALIDATION.map((v) => (
            <article key={v.id} className="rounded-[20px] bg-paper-sunken/70 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={v.result === "pass" ? "ok" : v.result === "partial" ? "warn" : "mark"}>{v.result}</Badge>
                <span className="text-sm font-medium">{v.requirement}</span>
              </div>
              <p className="mt-2 text-sm">{v.page}</p>
              <p className="text-xs text-ink-subtle">{v.url}</p>
              <p className="mt-2 text-sm leading-6 text-ink-muted">کار: {v.task}</p>
              <p className="text-sm leading-6 text-ink-muted">اعتماد: {v.trust}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">سیزده بند بستن</h2>
        <dl className="mt-4 flex flex-col gap-3">
          {(
            [
              ["شکاف ها", DELIVERABLE.gaps],
              ["زیرساخت", DELIVERABLE.infrastructure],
              ["تعمیر E-E-A-T", DELIVERABLE.eeat],
              ["ارزش افزوده", DELIVERABLE.original],
              ["UX", DELIVERABLE.ux],
              ["تعامل", DELIVERABLE.interactive],
              ["دسترسی", DELIVERABLE.a11y],
              ["چندرسانه ای", DELIVERABLE.media],
              ["اسکیما", DELIVERABLE.schema],
              ["اندازه گیری هوش مصنوعی", DELIVERABLE.aiMeasure],
              ["کارخانه", DELIVERABLE.factory],
              ["عمدا ساخته نشد", DELIVERABLE.notDone],
              ["مانع", DELIVERABLE.blockers],
            ] as const
          ).map(([k, items]) => (
            <div key={k} className="rounded-[16px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <dt className="text-sm font-medium">{k}</dt>
              {items.map((x) => (
                <dd key={x} className="mt-1 text-sm leading-7 text-ink-muted">
                  {x}
                </dd>
              ))}
            </div>
          ))}
        </dl>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">تکنیک تازه — هنوز بهترین عمل نیست</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {TECHNIQUES.map((t) => (
            <li key={t.id} className="rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6">
              <Badge>{t.status}</Badge>
              <p className="mt-2 font-medium">{t.name}</p>
              <p className="text-ink-muted">{t.evidence}</p>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">نمونه فرزندان ماشین حساب</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {CALCULATOR_CHILDREN.map((c) => (
            <li key={c.id} className="rounded-[16px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <p className="font-medium">{c.title}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{c.note}</p>
              <p className="mt-1 text-xs text-ink-subtle">
                روش {c.methodologySeen} · {c.action}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link to="/factory/intake">
          <Button>دریافت تجربه دست اول</Button>
        </Link>
        <Link to="/factory/pages">
          <Button variant="secondary">ممیزی صفحات</Button>
        </Link>
      </div>
    </main>
  );
}
