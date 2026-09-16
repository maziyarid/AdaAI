import { createFileRoute, Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ACTIONS,
  CHANGELOG,
  COVERAGE,
  FINDINGS,
  FLOW,
  PRINCIPLES,
  REJECTS,
  SITES,
} from "@/lib/seo/data";

export const Route = createFileRoute("/factory/")({ component: FactoryHome });

function FactoryHome() {
  const sh = COVERAGE.sources[0];
  const community = COVERAGE.sources[1];
  const now = FINDINGS.filter((f) => f.actionability === "now").length;
  const rejected = FINDINGS.filter((f) => f.actionability === "reject").length;
  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">حافظه سئو · لایه تصمیم</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">کارخانه محتوا تصمیم می گیرد، قلم می نویسد.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          تجربه عملی سئوی فارسی اینجا به قانون شرطی تبدیل می شود. هیچ پستی از تلگرام مستقیم مقاله نمی شود. نگارش همچنان روی قلم و کتابچه است.
        </p>
      </header>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { k: "پست شهرام", v: String(sh.inspected) },
          { k: "یافته ساخت یافته", v: String(FINDINGS.length) },
          { k: "الان قابل اجرا", v: String(now) },
          { k: "نپذیرید", v: String(rejected) },
        ].map((x) => (
          <div key={x.k} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
            <p className="font-display text-2xl font-semibold">{x.v}</p>
            <p className="mt-1 text-xs text-ink-muted">{x.k}</p>
          </div>
        ))}
      </section>

      <section className="rounded-[24px] bg-mark/8 p-5">
        <h2 className="font-display text-xl font-semibold">شکاف پوشش</h2>
        <p className="mt-2 leading-7 text-ink-muted">{community.inaccessible}</p>
        <p className="mt-2 text-sm leading-6 text-ink-muted">
          پاسخ های نقل شده در کانال شهرام به عنوان وکیل پرسش و پاسخ ثبت شده اند، نه به عنوان تاریخ کامل گروه. ویدئوهای مرادی رونوشت ندارند.
        </p>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">چرخه ورود دانش</h2>
        <ol className="mt-4 flex flex-col gap-2">
          {FLOW.map((step, i) => (
            <li key={step} className="flex gap-3 rounded-[16px] bg-paper-sunken/70 px-4 py-3 text-sm leading-6">
              <span className="font-mono text-xs text-ink-subtle">{String(i + 1).padStart(2, "0")}</span>
              <span>{step}</span>
            </li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">اصول جاری</h2>
        <ol className="mt-4 flex flex-col gap-2">
          {PRINCIPLES.map((p, i) => (
            <li key={p} className="flex gap-3 rounded-[16px] bg-paper-sunken/70 px-4 py-3 text-sm leading-6">
              <span className="font-mono text-xs text-ink-subtle">{String(i + 1).padStart(2, "0")}</span>
              <span>{p}</span>
            </li>
          ))}
        </ol>
      </section>

      <section>
        <div className="flex items-end justify-between gap-3">
          <h2 className="font-display text-2xl font-semibold">اقدام فوری</h2>
          <Link to="/factory/queue" className="text-sm text-slate hover:underline">
            صف کامل
          </Link>
        </div>
        <ul className="mt-4 flex flex-col gap-3">
          {ACTIONS.filter((a) => a.priority === "P0").map((a) => (
            <li key={a.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <Badge tone="mark">{a.priority}</Badge>
              <p className="mt-2 font-medium">{a.title}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{a.why}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
        <h2 className="font-display text-xl font-semibold">نمایه سایت در این جعبه ابزار</h2>
        {SITES.map((s) => (
          <div key={s.id} className="mt-3">
            <p className="font-medium">{s.domain}</p>
            <p className="mt-1 text-sm leading-6 text-ink-muted">{s.role}</p>
            <p className="mt-2 text-sm leading-6 text-ink-muted">{s.notes}</p>
          </div>
        ))}
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">نمونه نپذیرید</h2>
        <ul className="mt-4 grid gap-2 sm:grid-cols-2">
          {REJECTS.slice(0, 6).map((r) => (
            <li key={r.id} className="rounded-[16px] bg-paper-sunken/70 px-4 py-3 text-sm leading-6">
              <span className="font-mono text-xs text-ink-subtle">{r.id}</span>
              <p className="mt-1">{r.title}</p>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-sm text-ink-muted">فهرست کامل در تعارض و صف.</p>
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">لایه سودمندی</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {[
            { to: "/factory/trust" as const, t: "اعتماد", d: "رجیستری نقش، سیاست، ریست اسکیما. نمره E-E-A-T نیست." },
            { to: "/factory/pages" as const, t: "صفحات", d: "ممیزی کار کاربر روی URL زنده. پیش فرض حفظ است." },
            { to: "/factory/ux" as const, t: "تجربه", d: "زبان رابط، دسترسی، ابزار تصمیم، تجربه دست اول." },
            { to: "/factory/intel" as const, t: "پژوهش", d: "خوشه رویداد گوگل. تیتر صنعت وارد تولید نمی شود." },
            { to: "/factory/os" as const, t: "وضعیت", d: "شکاف ها بسته، صف، پذیرفته یا مسدودند. نمره واحد نیست." },
            { to: "/factory/intake" as const, t: "تجربه دست اول", d: "حکایت قانون نمی شود. درگاه ارزش افزوده برای نشانی تازه." },
          ].map((x) => (
            <Link
              key={x.to}
              to={x.to}
              className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]"
            >
              <p className="font-medium">{x.t}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{x.d}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="text-sm leading-6 text-ink-subtle">
        آخرین تغییر کارخانه: {CHANGELOG[CHANGELOG.length - 1]?.at} · {CHANGELOG.length} بند دفتر تغییر. شیت زنده بیرون این پیش نمایش دست نخورده است؛ اینجا لایه افزودنی مدل شده.
      </section>

      <div className="flex flex-wrap gap-3">
        <Link to="/factory/corpus">
          <Button>پیکره را بگردید</Button>
        </Link>
        <Link to="/desk">
          <Button variant="secondary">برگردید به میز نگارش</Button>
        </Link>
      </div>
    </main>
  );
}
