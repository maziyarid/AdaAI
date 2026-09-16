import { createFileRoute } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { CONTRIBUTORS, ORG, PAGE_ROLE_EEAT, POLICIES, SCHEMA_RULES, WHO_HOW_WHY } from "@/lib/seo/data";

export const Route = createFileRoute("/factory/trust")({ component: TrustPage });

const V: Record<string, { label: string; tone: "warn" | "mark" | "ok" | "slate" | "ink" }> = {
  identity_incomplete: { label: "هویت ناقص", tone: "warn" },
  unassigned: { label: "خالی", tone: "mark" },
  unverified: { label: "تأیید نشده", tone: "warn" },
  verified: { label: "تأیید شده", tone: "ok" },
  do_not_use: { label: "استفاده نشود", tone: "mark" },
  missing: { label: "نیست", tone: "mark" },
  fragmented: { label: "پراکنده", tone: "warn" },
  exists_weak: { label: "هست و ضعیف", tone: "warn" },
  adequate: { label: "کافی", tone: "ok" },
};

function TrustPage() {
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">شاهد اعتماد · نه نمره</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">اعتماد را نمی نویسیم؛ نشان می دهیم.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          E-E-A-T درصد نیست. نام جعلی نمی گذاریم. مدرک اختراع نمی شود. سازمان بی نام بهتر از فرد دروغین است.
        </p>
      </header>

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
        <h2 className="font-display text-xl font-semibold">{ORG.brand}</h2>
        <dl className="mt-4 grid gap-3 text-sm leading-6 sm:grid-cols-2">
          <Item k="دامنه" v={ORG.domain} />
          <Item k="تماس کانونی زنده" v={ORG.contactOwner} />
          <Item k="روش های تماس" v={ORG.contactMethodsUrl} />
          <Item k="تماس عمومی دیده شده" v={ORG.publicContact} />
          <Item k="نام حقوقی" v={ORG.legalName} />
          <Item k="نشانی" v={ORG.address} />
          <Item k="قلمرو" v={ORG.specialisation} />
          <Item k="سایت خواهر" v={ORG.sisterSites} />
        </dl>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">چه / چگونه / چرا</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <article className="rounded-[20px] bg-paper-sunken/70 p-4">
            <h3 className="font-medium">چه کسی</h3>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{WHO_HOW_WHY.who}</p>
          </article>
          <article className="rounded-[20px] bg-paper-sunken/70 p-4">
            <h3 className="font-medium">چگونه</h3>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{WHO_HOW_WHY.how}</p>
          </article>
          <article className="rounded-[20px] bg-paper-sunken/70 p-4">
            <h3 className="font-medium">چرا</h3>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{WHO_HOW_WHY.why}</p>
          </article>
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">رجیستری نقش</h2>
        <div className="mt-4 flex flex-col gap-3">
          {CONTRIBUTORS.map((c) => (
            <article key={c.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs text-ink-subtle">{c.id}</span>
                <Badge tone={V[c.verification]?.tone ?? "ink"}>{V[c.verification]?.label ?? c.verification}</Badge>
              </div>
              <h3 className="mt-2 font-display text-lg font-semibold">{c.name}</h3>
              <p className="text-sm text-ink-muted">{c.role}</p>
              <p className="mt-2 text-sm leading-7">{c.notes}</p>
              <p className="mt-2 text-sm leading-6 text-ink-muted">مدرک: {c.credentials}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">نقش صفحه</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {PAGE_ROLE_EEAT.map((r) => (
            <article key={r.role} className="rounded-[20px] bg-paper-sunken/70 p-4 text-sm leading-6">
              <p className="font-medium">{r.role}</p>
              <p className="mt-2 text-ink-muted">لازم: {r.need.join("؛ ")}</p>
              <p className="mt-2 text-ink-muted">نه: {r.notNeed}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">سیاست ها</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {POLICIES.map((p) => (
            <li key={p.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone={V[p.status]?.tone ?? "ink"}>{V[p.status]?.label ?? p.status}</Badge>
                <span className="font-medium">{p.title}</span>
              </div>
              <p className="mt-2 text-sm leading-6 text-ink-muted">{p.neededBecause}</p>
              <ul className="mt-2 list-disc pr-5 text-sm leading-6 text-ink-muted">
                {p.outline.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">ریست اسکیما</h2>
        <div className="mt-4 flex flex-col gap-3">
          {SCHEMA_RULES.map((s) => (
            <article key={s.id} className="rounded-[20px] bg-paper-sunken/70 p-4 text-sm leading-6">
              <p className="font-medium">{s.type}</p>
              <p className="mt-1 text-ink-muted">وقتی: {s.useWhen}</p>
              <p className="text-ink-muted">هرگز: {s.never}</p>
              <p className="mt-1 text-ink-subtle">{s.googleStatus}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function Item({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-subtle">{k}</dt>
      <dd className="mt-0.5 text-ink-muted">{v}</dd>
    </div>
  );
}
