import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { COMPACT, REGISTERS } from "@/lib/content";
import { FINDINGS, PRINCIPLES } from "@/lib/seo/data";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <main className="flex flex-col gap-12">
      <section className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
        <div className="flex flex-col gap-5">
          <Badge tone="slate">Art of Writing Bible · v2.0</Badge>
          <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.15] text-ink sm:text-5xl">
            روشن ترین حرف راست، به فارسی ایرانی، به رجیستری که خواننده به آن اعتماد دارد.
          </h1>
          <p className="max-w-xl text-lg leading-8 text-ink-muted">{COMPACT}</p>
          <div className="flex flex-wrap gap-3">
            <Link to="/desk">
              <Button size="lg">میز ویرایش را باز کنید</Button>
            </Link>
            <Link to="/factory">
              <Button size="lg" variant="secondary">
                کارخانه سئو
              </Button>
            </Link>
          </div>
        </div>
        <aside className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
          <p className="text-xs font-medium tracking-wide text-ink-subtle">آنچه این کارگاه نمی کند</p>
          <ul className="mt-4 flex flex-col gap-3 text-sm leading-6 text-ink-muted">
            <li>صدای هیچ نویسنده زنده ای را شبیه سازی نمی کند.</li>
            <li>برای فریب آشکارساز، ترکیدن و غلط عمدی نمی سازد.</li>
            <li>نثر مجله را روی صفحه SPSS نمی ریزد و دری را با فارسی ایران قاطی نمی کند.</li>
            <li>ادعا را به صرف طبیعی بودن جمله، واقعیت نمی شمارد.</li>
          </ul>
        </aside>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:items-stretch">
        <Link
          to="/factory"
          className="rounded-[24px] bg-slate p-6 text-slate-fg shadow-[var(--shadow-border)] transition-transform duration-150 hover:opacity-95"
        >
          <Badge tone="ink">حافظه سئو</Badge>
          <h2 className="mt-3 font-display text-2xl font-semibold">کارخانه تصمیم می گیرد، قلم می نویسد.</h2>
          <p className="mt-3 max-w-lg text-sm leading-7 text-slate-fg/80">
            {FINDINGS.length} یافته میدانی از کانال های سئوی فارسی، با تعارض، آزمایش، و دفتر نپذیرید. هیچ پستی مستقیم مقاله نمی شود.
          </p>
          <p className="mt-4 text-sm font-medium">ورود به کارخانه</p>
        </Link>
        <Link
          to="/tools/stat-test"
          className="rounded-[24px] bg-paper-elevated p-6 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]"
        >
          <Badge tone="ok">ابزار تصمیم</Badge>
          <h2 className="mt-3 font-display text-2xl font-semibold">کدام آزمون را باید در نظر بگیرم؟</h2>
          <p className="mt-3 text-sm leading-7 text-ink-muted">
            غربال آموزشی با حد صریح. متن جدول حتی اگر اسکریپت خاموش باشد خواندنی است. جایگزین مشاور نیست.
          </p>
          <p className="mt-4 text-sm font-medium text-slate">باز کردن انتخاب آزمون</p>
        </Link>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <Link
          to="/tools/feasibility"
          className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]"
        >
          <h2 className="font-display text-lg font-semibold">امکان سنجی موضوع</h2>
          <p className="mt-2 text-sm leading-6 text-ink-muted">پرچم خطر. نمره امکان نیست.</p>
        </Link>
        <Link
          to="/tools/questionnaire"
          className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]"
        >
          <h2 className="font-display text-lg font-semibold">غربال پرسشنامه</h2>
          <p className="mt-2 text-sm leading-6 text-ink-muted">نقص رایج قبل از نمونه اصلی.</p>
        </Link>
        <Link to="/factory/os" className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <h2 className="font-display text-lg font-semibold">وضعیت سامانه</h2>
          <p className="mt-2 text-sm leading-6 text-ink-muted">شکاف ماده صف دارد یا پذیرفته شده است.</p>
        </Link>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:items-stretch">
        <div className="rounded-[24px] bg-paper-sunken/70 p-6 lg:col-span-2">
          <p className="text-xs text-ink-subtle">اصل جاری</p>
          <p className="mt-3 font-display text-lg font-semibold leading-8">{PRINCIPLES[0]}</p>
          <p className="mt-3 text-sm leading-7 text-ink-muted">{PRINCIPLES[3]}</p>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:items-stretch">
        <Link
          to="/ada"
          className="rounded-[24px] bg-paper-elevated p-6 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]"
        >
          <Badge tone="ok">حافظه قطعی</Badge>
          <h2 className="mt-3 font-display text-2xl font-semibold">Ada قبل از نوشتن، P0 را بار می کند.</h2>
          <p className="mt-3 text-sm leading-7 text-ink-muted">
            پایگاه PostgreSQL آماده است. فکر به فارسی ایرانی و ممنوعیت دری سیاست اجباری است، نه شباهت معنایی.
          </p>
          <p className="mt-4 text-sm font-medium text-slate">باز کردن حافظه Ada</p>
        </Link>
        <Link
          to="/desk"
          search={{ register: "LANDING_PRODUCT" }}
          className="rounded-[24px] bg-paper-elevated p-6 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]"
        >
          <Badge tone="warn">رجیستر لندینگ</Badge>
          <h2 className="mt-3 font-display text-2xl font-semibold">لندینگ را با چکیده مجله ننویسید.</h2>
          <p className="mt-3 text-sm leading-7 text-ink-muted">
            کار در اولین صفحه. دکمه نام عمل است. پوهنتون و اکوسیستم اینجا قاطی نمی شوند.
          </p>
          <p className="mt-4 text-sm font-medium text-slate">سنجش نمونه لندینگ</p>
        </Link>
      </section>

      <section className="flex flex-col gap-5">
        <div className="flex items-end justify-between gap-4">
          <h2 className="font-display text-2xl font-semibold">نقشه کامل رجیستر</h2>
          <Link to="/registers" className="text-sm text-slate hover:underline">
            جزئیات
          </Link>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {REGISTERS.map((r) => (
            <Link
              key={r.id}
              to="/desk"
              search={{ register: r.id }}
              className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]"
            >
              <p className="font-medium text-ink">{r.name}</p>
              <p className="mt-1 text-sm leading-6 text-ink-muted">{r.use}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          {
            t: "حرکت ذهنی خواننده",
            d: "هر بند باید واقعیت، تمایز، سازوکار، مثال، حد، یا تصمیم اضافه کند. بازنویسی همان حرف با مترادف عمق نیست.",
          },
          {
            t: "فعل، نه پرستیژ",
            d: "بررسی شد از مورد بررسی قرار گرفتن روشن تر است. در فصل روش مجهول بی کنشگر قرارداد است؛ در راهنما فعل مستقیم.",
          },
          {
            t: "فکر روی صفحه",
            d: "نوسان طول جمله، پرسش لولا، مثال محلی، و اعتراف به حد — اگر کسی دارد فکر می کند ظاهر می شوند. تزریق نکنید.",
          },
        ].map((card) => (
          <article key={card.t} className="rounded-[20px] bg-paper-sunken/60 p-5">
            <h3 className="font-display text-lg font-semibold">{card.t}</h3>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{card.d}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
